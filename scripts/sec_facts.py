#!/usr/bin/env python3
"""SEC EDGAR 财务序列 — 美股一手财务数据取数（免费，无需 key）。

用法:
    python3 scripts/sec_facts.py MU                 # 最近 8 个季度：营收/毛利率/营业利润率/capex/经营现金流/FCF
    python3 scripts/sec_facts.py MU --quarters 12
    python3 scripts/sec_facts.py MU --json
    python3 scripts/sec_facts.py --capex            # 云厂商 capex 序列 + YoY + 二阶导（默认 MSFT GOOGL AMZN META ORCL）
    python3 scripts/sec_facts.py --capex MSFT META  # 指定公司

数据源:
    - https://www.sec.gov/files/company_tickers.json（ticker → CIK）
    - https://data.sec.gov/api/xbrl/companyfacts/CIK##########.json（XBRL 全量事实）
    SEC 要求 User-Agent 带联系方式：设置环境变量 SEC_USER_AGENT="<名字或项目> <邮箱>"；
    未设置时用占位 UA（可用但不规范，长期使用请自行设置）。skill 不内置任何个人联系方式。

口径说明:
    - 季度值优先取 10-Q/10-K 中约 3 个月的期间；现金流量表只披露年初至今累计（YTD）→ 用相邻 YTD 相减还原单季。
    - 第 4 财季 = 全年（10-K）− 前三季 YTD；若 10-K 尚未提交（只有 8-K 新闻稿），该季缺失，以新闻稿为准。
    - 季度按「期末日期」排序；财年非自然年的公司（MU / NVDA / ORCL / MSFT）请对照 fp 列。
    - 数字为 XBRL 申报原值（美元），未做 non-GAAP 调整。

退出码: 0 = 成功, 3 = ticker 不在 SEC 列表（非美国申报人，如 SK Hynix → 用 DART）, 2 = 网络/解析错误。
"""
import argparse
import datetime as dt
import json
import os
import sys
import urllib.error
import urllib.request

UA = os.environ.get("SEC_USER_AGENT", "stocks-ai-taste-skill research contact@example.com")
TICKERS_URL = "https://www.sec.gov/files/company_tickers.json"
FACTS_URL = "https://data.sec.gov/api/xbrl/companyfacts/CIK{cik:010d}.json"
HYPERSCALERS = ["MSFT", "GOOGL", "AMZN", "META", "ORCL"]

# 每个指标按顺序尝试的 us-gaap 概念（公司间命名不同）
CONCEPTS = {
    "revenue": ["RevenueFromContractWithCustomerExcludingAssessedTax", "Revenues",
                "RevenueFromContractWithCustomerIncludingAssessedTax", "SalesRevenueNet"],
    "gross_profit": ["GrossProfit"],
    "cost_of_revenue": ["CostOfRevenue", "CostOfGoodsAndServicesSold"],
    "operating_income": ["OperatingIncomeLoss"],
    "capex": ["PaymentsToAcquirePropertyPlantAndEquipment", "PaymentsToAcquireProductiveAssets"],
    "cfo": ["NetCashProvidedByUsedInOperatingActivities"],
}


def _get(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Encoding": "identity"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def cik_of(ticker):
    for row in _get(TICKERS_URL).values():
        if row["ticker"].upper() == ticker.upper().replace(".", "-"):
            return int(row["cik_str"]), row["title"]
    return None, None


def _days(start, end):
    return (dt.date.fromisoformat(end) - dt.date.fromisoformat(start)).days


def _periods(facts, concept):
    """{(start, end): (val, fp, filed)}，同一期间保留最新申报（含重述）。"""
    units = facts.get("us-gaap", {}).get(concept, {}).get("units", {}).get("USD", [])
    out = {}
    for u in units:
        if u.get("form") not in ("10-Q", "10-K", "10-Q/A", "10-K/A") or "start" not in u:
            continue
        key = (u["start"], u["end"])
        if key not in out or u["filed"] > out[key][2]:
            out[key] = (u["val"], u.get("fp"), u["filed"])
    return out


def quarterly(facts, concept):
    """{end: (val, fp)} 单季序列：直接取 ~3 个月期间，否则用 YTD 相减还原。"""
    periods = _periods(facts, concept)
    q = {}
    for (start, end), (val, fp, _) in periods.items():
        if 80 <= _days(start, end) <= 100:
            q[end] = (val, fp)
    # YTD 还原：同一 start 的累计期间按 end 排序，相邻相减
    by_start = {}
    for (start, end), (val, fp, _) in periods.items():
        if _days(start, end) > 100:
            by_start.setdefault(start, []).append((end, val, fp))
    for start, rows in by_start.items():
        rows.sort()
        prev_end, prev_val = None, None
        # 第一段（~6 个月）减去以同一 start 开始的单季
        for end, val, fp in rows:
            if prev_end is None:
                first_q = [(e, v) for (s, e), (v, _, _) in periods.items()
                           if s == start and 80 <= _days(s, e) <= 100]
                if first_q:
                    prev_end, prev_val = first_q[0]
            if prev_end is not None and end not in q and 80 <= _days(prev_end, end) <= 100:
                q[end] = (val - prev_val, fp)
            prev_end, prev_val = end, val
    return q


def series(facts, metric):
    """在候选概念中取「最近一期最新」的那个（公司会换标签，如 AMZN 2017 后改用 ProductiveAssets）。"""
    best, best_concept = {}, None
    for concept in CONCEPTS[metric]:
        q = quarterly(facts, concept)
        if q and (not best or (max(q), len(q)) > (max(best), len(best))):
            best, best_concept = q, concept
    return {end: (val, "Q4" if fp == "FY" else fp) for end, (val, fp) in best.items()}, best_concept


def company_table(ticker, n):
    cik, title = cik_of(ticker)
    if cik is None:
        return None
    facts = _get(FACTS_URL.format(cik=cik))["facts"]
    data = {m: series(facts, m) for m in CONCEPTS}
    rev = data["revenue"][0]
    ends = sorted(rev)[-n:]
    rows = []
    for end in ends:
        r = rev[end][0]
        gp = data["gross_profit"][0].get(end, (None,))[0]
        if gp is None and end in data["cost_of_revenue"][0]:
            gp = r - data["cost_of_revenue"][0][end][0]
        oi = data["operating_income"][0].get(end, (None,))[0]
        capex = data["capex"][0].get(end, (None,))[0]
        cfo = data["cfo"][0].get(end, (None,))[0]
        rows.append({
            "period_end": end,
            "fp": rev[end][1],
            "revenue": r,
            "gross_margin_pct": round(gp / r * 100, 1) if gp is not None and r else None,
            "op_margin_pct": round(oi / r * 100, 1) if oi is not None and r else None,
            "capex": capex,
            "cfo": cfo,
            "fcf": cfo - capex if cfo is not None and capex is not None else None,
            "capex_to_revenue_pct": round(capex / r * 100, 1) if capex is not None and r else None,
        })
    # 营收 YoY（同表内 4 个季度前）
    full = sorted(rev)
    for row in rows:
        i = full.index(row["period_end"])
        if i >= 4:
            prev = rev[full[i - 4]][0]
            row["revenue_yoy_pct"] = round((row["revenue"] / prev - 1) * 100, 1) if prev else None
    return {"ticker": ticker.upper(), "cik": cik, "name": title,
            "concepts": {m: c for m, (_, c) in data.items()}, "quarters": rows,
            "source": f"SEC EDGAR companyfacts CIK{cik:010d}"}


def capex_table(tickers, n=8):
    out = []
    for t in tickers:
        cik, title = cik_of(t)
        if cik is None:
            out.append({"ticker": t, "error": "不在 SEC 列表"})
            continue
        facts = _get(FACTS_URL.format(cik=cik))["facts"]
        q, concept = series(facts, "capex")
        ends = sorted(q)
        rows = []
        for i, end in enumerate(ends):
            yoy = None
            if i >= 4 and q[ends[i - 4]][0]:
                yoy = round((q[end][0] / q[ends[i - 4]][0] - 1) * 100, 1)
            rows.append({"period_end": end, "fp": q[end][1], "capex": q[end][0], "yoy_pct": yoy})
        # TTM（近 4 季滚动）降噪：单季 YoY 受交付节奏影响大，二阶导以 TTM YoY 的变化为准
        for i in range(len(rows)):
            if i >= 3:
                rows[i]["ttm"] = sum(r["capex"] for r in rows[i - 3:i + 1])
            if i >= 7 and rows[i - 4].get("ttm"):
                rows[i]["ttm_yoy_pct"] = round((rows[i]["ttm"] / rows[i - 4]["ttm"] - 1) * 100, 1)
        for i in range(1, len(rows)):
            a, b = rows[i - 1].get("ttm_yoy_pct"), rows[i].get("ttm_yoy_pct")
            rows[i]["ttm_yoy_change_pp"] = round(b - a, 1) if a is not None and b is not None else None
        out.append({"ticker": t, "name": title, "concept": concept, "quarters": rows[-n:]})
    return out


def _b(x):
    return f"{x / 1e9:,.2f}" if isinstance(x, (int, float)) else "—"


def _p(x, signed=False):
    if x is None:
        return "—"
    return f"{x:+.1f}%" if signed else f"{x:.1f}%"


def render_company(d):
    L = [f"# {d['ticker']} · {d['name']} · 季度财务（单位 $B，{d['source']}）", "",
         "| 期末 | fp | 营收 | YoY | 毛利率 | 营业利润率 | capex | capex/营收 | 经营现金流 | FCF |",
         "|---|---|---|---|---|---|---|---|---|---|"]
    for r in d["quarters"]:
        L.append(f"| {r['period_end']} | {r['fp']} | {_b(r['revenue'])} | {_p(r.get('revenue_yoy_pct'), True)} "
                 f"| {_p(r['gross_margin_pct'])} | {_p(r['op_margin_pct'])} | {_b(r['capex'])} "
                 f"| {_p(r['capex_to_revenue_pct'])} | {_b(r['cfo'])} | {_b(r['fcf'])} |")
    missing = [m for m, c in d["concepts"].items() if c is None]
    if missing:
        L.append(f"\n缺失概念（该公司未用标准标签）：{', '.join(missing)}")
    L.append("\n注：第 4 财季须 10-K 提交后才有；最新一季若只有 8-K 新闻稿，以新闻稿为准。")
    return "\n".join(L)


def render_capex(rows):
    L = ["# Hyperscaler capex 序列（SEC EDGAR，单位 $B）", "",
         "二阶导 = TTM（近 4 季）capex YoY 增速的季度变化（pp）；连续 2 季为负 = 增速放缓 → 卖铲子环节估值承压"
         "（见 chain_derate_triggers）。单季 YoY 噪声大，仅作参考。", ""]
    for c in rows:
        if "error" in c:
            L.append(f"## {c['ticker']}：{c['error']}\n")
            continue
        L += [f"## {c['ticker']} · {c['name']}（{c['concept']}）", "",
              "| 期末 | fp | 单季 capex | 单季 YoY | TTM capex | TTM YoY | 二阶导(TTM) |", "|---|---|---|---|---|---|---|"]
        for r in c["quarters"]:
            chg = r.get("ttm_yoy_change_pp")
            L.append(f"| {r['period_end']} | {r['fp']} | {_b(r['capex'])} | {_p(r['yoy_pct'], True)} "
                     f"| {_b(r.get('ttm'))} | {_p(r.get('ttm_yoy_pct'), True)} "
                     f"| {'—' if chg is None else f'{chg:+.1f}pp'} |")
        L.append("")
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("tickers", nargs="*")
    ap.add_argument("--capex", action="store_true", help="云厂商 capex 二阶导跟踪")
    ap.add_argument("--quarters", type=int, default=8)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    try:
        if args.capex:
            d = capex_table(args.tickers or HYPERSCALERS, args.quarters)
            print(json.dumps(d, ensure_ascii=False, indent=2) if args.json else render_capex(d))
            return
        if len(args.tickers) != 1:
            ap.error("需要一个 ticker，或使用 --capex")
        d = company_table(args.tickers[0], args.quarters)
    except (urllib.error.URLError, ValueError, KeyError) as e:
        print(f"取数失败: {e}", file=sys.stderr)
        sys.exit(2)

    if d is None:
        print(f"{args.tickers[0].upper()} 不在 SEC 申报人列表（非美国公司请用 DART / 公开资讯观测站 / TDnet）。",
              file=sys.stderr)
        sys.exit(3)
    print(json.dumps(d, ensure_ascii=False, indent=2) if args.json else render_company(d))


if __name__ == "__main__":
    main()
