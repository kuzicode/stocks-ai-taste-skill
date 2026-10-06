#!/usr/bin/env python3
"""thesis 复盘 — 把历史 4 维 thesis 与之后的实际走势对照，产出命中表（review 模式的机检底座）。

用法:
    python3 scripts/review_theses.py                       # 复盘 examples/*.yaml，打印 Markdown
    python3 scripts/review_theses.py examples/nvda_*.yaml  # 指定文件
    python3 scripts/review_theses.py --write               # 另存 reports/<今天>_thesis复盘_US.md

每份 thesis（按其 as_of_date）:
    1. 90 天窗口：已结束 / 进行中；窗口内 catalyst 是否已发生
    2. 价格档位：窗口末（或最新）收盘落在 bear / base / bull 哪档，或档外
    3. 方向：view=bull/bear 与窗口收益是否同向（neutral/watching 不计）
    4. 短期计划（decision.short_term，方向为多/空时）：入场区是否触及；触及后先止损还是先止盈
       （日线粒度，同一根 K 线同时触及记为「同日双触」）
    5. 汇总：方向命中率、base 档命中率，按 confidence 分组 → 用来校准下一份 thesis 的 confidence

价格: Hyperliquid 日线（复用 hl_price.py 的 dex 选择与别名）。非美元计价（如 KRW）或未上 HL 的 thesis 标为「需现货」，
不硬比。结论只是复盘线索，不替代对 red_flag trigger 的人工核查。

退出码: 0 = 成功, 2 = 用法/解析/网络错误。
"""
import argparse
import datetime as dt
import glob
import os
import sys
import urllib.error

try:
    import yaml
except ImportError:
    print("需要 PyYAML：pip install pyyaml", file=sys.stderr)
    sys.exit(2)

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import hl_price  # noqa: E402
from validate_thesis import (  # noqa: E402
    direction_of,
    find_block,
    is_filled,
    parse_date,
    prices_of,
)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DAY_MS = 86400 * 1000
WINDOW_DAYS = 90


def price_range(value):
    nums = prices_of(value)
    if not nums:
        return None
    return (min(nums[:2]), max(nums[:2]))


def is_usd(value):
    text = str(value)
    return "$" in text and "KRW" not in text.upper()


def daily_closes(coin, start, end):
    """[(date, o, h, l, c)]，start/end 为 date（含）。"""
    s = int(dt.datetime.combine(start, dt.time(), dt.timezone.utc).timestamp() * 1000)
    e = int(dt.datetime.combine(end, dt.time(), dt.timezone.utc).timestamp() * 1000) + DAY_MS
    raw = hl_price._post({"type": "candleSnapshot", "req": {
        "coin": coin, "interval": "1d", "startTime": s, "endTime": e}}) or []
    out = []
    for c in raw:
        d = dt.datetime.fromtimestamp(c["t"] / 1000, dt.timezone.utc).date()
        out.append((d, float(c["o"]), float(c["h"]), float(c["l"]), float(c["c"])))
    return out


def classify(close, po):
    bands = [(k, price_range(po.get(f"{k}_90d"))) for k in ("bear", "base", "bull")]
    hits = [k for k, r in bands if r and r[0] <= close <= r[1]]
    if hits:
        return "/".join(hits)
    rs = [r for _, r in bands if r]
    if rs and close < min(r[0] for r in rs):
        return "低于 bear"
    if rs and close > max(r[1] for r in rs):
        return "高于 bull"
    return "档间空隙"


def short_term_outcome(st, candles):
    side = direction_of(st.get("direction", ""))
    entry, stop, tp = prices_of(st.get("entry", "")), prices_of(st.get("stop_loss", "")), prices_of(st.get("take_profit", ""))
    if not side or not entry:
        return "无多空计划（观望）"
    lo, hi = min(entry), max(entry)
    filled = None
    for i, (_, _, h, l, _) in enumerate(candles):
        if l <= hi and h >= lo:
            filled = i
            break
    if filled is None:
        return "入场区未触及"
    for d, _, h, l, _ in candles[filled:]:
        hit_stop = stop and (l <= max(stop) if side == "long" else h >= min(stop))
        hit_tp = tp and (h >= min(tp) if side == "long" else l <= max(tp))
        if hit_stop and hit_tp:
            return f"同日双触 {d}"
        if hit_stop:
            return f"止损 {d}"
        if hit_tp:
            return f"止盈 {d}"
    return "已入场，未触发止损/止盈"


def review(path, doc, today, cache):
    ticker = str(doc.get("ticker"))
    as_of = parse_date(doc.get("as_of_date"))
    po = doc.get("price_outlook") or {}
    view = str(doc.get("view", "")).lower()
    row = {
        "file": os.path.relpath(path, ROOT),
        "ticker": ticker,
        "as_of": as_of,
        "view": view,
        "confidence": str(doc.get("confidence", "")).lower(),
    }
    if not as_of:
        row["note"] = "缺 as_of_date，先跑 validate_thesis 补字段"
        return row

    horizon = as_of + dt.timedelta(days=WINDOW_DAYS)
    row["window"] = "已结束" if horizon <= today else f"进行中（至 {horizon}）"
    cats = [c for c in doc.get("catalysts_90d") or [] if isinstance(c, dict)]
    row["catalysts"] = "; ".join(
        f"{c.get('date')} {'✓' if (parse_date(c.get('date')) or today) <= today else '…'} {c.get('event', '')}"
        for c in cats
    )

    if not is_usd(po.get("current")):
        row["note"] = "非美元计价 → 需现货复盘"
        return row
    if ticker not in cache:
        try:
            cache[ticker] = hl_price.fetch(ticker, "auto", 0)
        except (urllib.error.URLError, ValueError, KeyError) as e:
            cache[ticker] = e
    live = cache[ticker]
    if not isinstance(live, dict):
        row["note"] = "未上 HL / 取数失败 → 需现货复盘"
        return row

    candles = daily_closes(live["coin"], as_of, min(horizon, today))
    if not candles:
        row["note"] = f"{live['coin']} 无窗口日线"
        return row
    entry_px = (prices_of(po.get("current")) or [None])[0]
    end_px = candles[-1][4]
    row.update({
        "coin": live["coin"],
        "entry_px": entry_px,
        "end_px": end_px,
        "now_px": live["mark"],
        "ret_pct": round((end_px / entry_px - 1) * 100, 1) if entry_px else None,
        "band": classify(end_px, po),
        "high": max(c[2] for c in candles),
        "low": min(c[3] for c in candles),
    })
    if view in ("bull", "bear") and row["ret_pct"] is not None:
        row["direction_hit"] = (row["ret_pct"] > 0) == (view == "bull")
    st = find_block(doc, "decision").get("short_term")
    if isinstance(st, dict):
        row["short_term"] = short_term_outcome(st, candles)
    return row


def render(rows, today):
    L = [f"# thesis 复盘（as of {today}）", "",
         "> 机检底座：`scripts/review_theses.py`。价格 = Hyperliquid 日线；窗口 = as_of_date + 90 天。"
         "非投资建议，结论须结合 red_flag trigger 人工复核。", "",
         "| 底稿 | as_of | view/conf | 窗口 | 当时价 | 窗口末价 | 收益 | 落档 | 方向 | 短期计划 | 最新价 |",
         "|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        if "end_px" not in r:
            L.append(f"| {r['file']} | {r['as_of']} | {r['view']}/{r['confidence']} | {r.get('window', '')} "
                     f"| — | — | — | — | — | — | {r.get('note', '')} |")
            continue
        hit = {True: "✓", False: "✗"}.get(r.get("direction_hit"), "—")
        L.append(f"| {r['file']} | {r['as_of']} | {r['view']}/{r['confidence']} | {r['window']} "
                 f"| ${r['entry_px']:g} | ${r['end_px']:g} | {r['ret_pct']:+.1f}% | {r['band']} | {hit} "
                 f"| {r.get('short_term', '—')} | ${r['now_px']:g} |")

    scored = [r for r in rows if "end_px" in r]
    L += ["", "## 汇总（按 confidence）", "", "| confidence | 份数 | 方向命中 | 落入 base 档 |", "|---|---|---|---|"]
    for conf in ("high", "medium", "low"):
        grp = [r for r in scored if r["confidence"] == conf]
        if not grp:
            continue
        dirs = [r["direction_hit"] for r in grp if "direction_hit" in r]
        base = sum("base" in r["band"] for r in grp)
        dir_txt = f"{sum(dirs)}/{len(dirs)}" if dirs else "—"
        L.append(f"| {conf} | {len(grp)} | {dir_txt} | {base}/{len(grp)} |")

    L += ["", "## catalyst 对照", ""]
    for r in rows:
        if r.get("catalysts"):
            L.append(f"- **{r['ticker']}（{r['as_of']}）**：{r['catalysts']}")
    L += ["", "## 下一步（review 模式）",
          "- 落档「低于 bear / 高于 bull」→ 情景设定过窄，下份 thesis 放宽或补情景；",
          "- 方向 ✗ 且 confidence=high/medium → 回查是哪条 support 失效、哪个 red_flag trigger 先触发，写进 docs/issues.md；",
          "- 窗口已结束的 thesis：按当前数据重写，或标记 superseded。"]
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="*")
    ap.add_argument("--as-of", default=None, help="复盘日（默认今天）")
    ap.add_argument("--write", action="store_true", help="写入 reports/<日期>_thesis复盘_US.md")
    args = ap.parse_args()

    today = dt.date.fromisoformat(args.as_of) if args.as_of else dt.date.today()
    paths = args.paths or sorted(glob.glob(os.path.join(ROOT, "examples", "*.yaml")))
    rows, cache = [], {}
    for p in paths:
        try:
            with open(p, encoding="utf-8") as f:
                docs = [d for d in yaml.safe_load_all(f) if is_filled(d)]
        except (OSError, yaml.YAMLError) as e:
            print(f"跳过 {p}: {e}", file=sys.stderr)
            continue
        for doc in docs:
            try:
                rows.append(review(p, doc, today, cache))
            except (urllib.error.URLError, ValueError, KeyError) as e:
                print(f"取数失败 {p}: {e}", file=sys.stderr)
                sys.exit(2)

    rows.sort(key=lambda r: (r["ticker"], str(r["as_of"])))
    md = render(rows, today)
    if args.write:
        out = os.path.join(ROOT, "reports", f"{today}_thesis复盘_US.md")
        with open(out, "w", encoding="utf-8") as f:
            f.write(md)
        print(f"已写入 {os.path.relpath(out, ROOT)}")
    else:
        print(md)


if __name__ == "__main__":
    main()
