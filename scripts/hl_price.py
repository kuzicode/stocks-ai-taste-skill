#!/usr/bin/env python3
"""Hyperliquid 美股 perp 价格取数 — skill 的价格主源（无需 API key）。

用法:
    python3 scripts/hl_price.py NVDA              # 人类可读速览（自动在各 HIP-3 dex 中找流动性最好的盘）
    python3 scripts/hl_price.py NVDA --json       # 机读 JSON
    python3 scripts/hl_price.py NVDA --candles 20 # 近 N 日线高低区间（默认 20）
    python3 scripts/hl_price.py NVDA --dex xyz    # 只查指定 dex（默认 auto）

数据源: POST https://api.hyperliquid.xyz/info（公开，无需 key）
    - perpDexs: 列出所有 HIP-3 部署方（xyz / flx / km / cash / mkts …）
    - metaAndAssetCtxs(dex=<d>): markPx / oraclePx / midPx / funding / maxLeverage / OI / dayNtlVlm / prevDayPx
    - candleSnapshot(coin=<d>:<T>, interval=1d): 日线 OHLCV → 区间、ATR14、MA50/MA200

dex 选择（--dex auto）:
    同一 ticker 可能在多个 dex 上市，冷门盘 OI=0 且价格过期（实测 2026-10 flx/km/cash:NVDA 偏离 xyz 13-18%）。
    → 按「日成交额，其次 OI 名义值」选最活跃的盘；其余盘列在 alternatives 里，零 OI 的标记为 stale。

别名: SKHYNIX→SKHX（本地股美元 perp）；SKHY 为 2026-07 新上的 ADR perp，两者价格口径不同，勿混用。

funding 为 Hyperliquid **每小时**资金费率；年化 = funding × 24 × 365。
基差提示: mark 相对 oracle 的偏离；美股休市时段（周末/盘后）oracle 不由现货连续驱动，价格仅作参考，
    进入结论前须用现货收盘价交叉核对。

退出码:
    0 = 成功
    3 = 该 ticker 不在任何 Hyperliquid dex（或不在指定 dex）→ 调用方应回退 WebSearch 取现货价
    2 = 网络/解析错误或用法错误
"""
import argparse
import datetime as dt
import json
import sys
import urllib.error
import urllib.request
from zoneinfo import ZoneInfo

API = "https://api.hyperliquid.xyz/info"
DAY_MS = 86400 * 1000
DEFAULT_DEX_ORDER = ["xyz"]  # 流动性打平时优先 xyz（HIP-3 股票 OI 90%+）
ALIASES = {"SKHYNIX": "SKHX", "SK-HYNIX": "SKHX", "000660": "SKHX", "000660.KS": "SKHX"}
NY = ZoneInfo("America/New_York")


def _post(body):
    req = urllib.request.Request(
        API,
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.load(r)


def _f(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def list_dexes():
    names = [d["name"] for d in _post({"type": "perpDexs"}) if d and d.get("name")]
    return sorted(names, key=lambda n: (n not in DEFAULT_DEX_ORDER, names.index(n)))


def _market(dex, symbol):
    """返回 (asset, ctx) 或 None。"""
    coin = f"{dex}:{symbol}"
    meta, ctxs = _post({"type": "metaAndAssetCtxs", "dex": dex})
    for asset, ctx in zip(meta.get("universe", []), ctxs):
        if asset.get("name") == coin:
            return asset, ctx
    return None


def us_session(now_utc):
    """粗略判断美股常规交易时段（不含节假日）：regular / extended / closed。"""
    ny = now_utc.astimezone(NY)
    if ny.weekday() >= 5:
        return "closed"
    minutes = ny.hour * 60 + ny.minute
    if 9 * 60 + 30 <= minutes < 16 * 60:
        return "regular"
    if 4 * 60 <= minutes < 20 * 60:
        return "extended"
    return "closed"


def _candle_stats(coin, n_candles):
    end = int(dt.datetime.now(dt.timezone.utc).timestamp() * 1000) + DAY_MS
    start = end - 230 * DAY_MS  # 够算 MA200 + ATR14
    candles = _post({"type": "candleSnapshot", "req": {
        "coin": coin, "interval": "1d", "startTime": start, "endTime": end}}) or []
    if not candles:
        return None
    closes = [_f(c["c"]) for c in candles]
    recent = candles[-n_candles:] if n_candles > 0 else []
    out = {"history_days": len(candles), "last_close": closes[-1]}
    if recent:
        out.update({
            "n": len(recent),
            "range_high": max(_f(c["h"]) for c in recent),
            "range_low": min(_f(c["l"]) for c in recent),
            "first_open": _f(recent[0]["o"]),
        })
    # ATR14（Wilder 简化为均值）— 短期仓位按 ATR × 单笔风险 % 计算
    if len(candles) >= 15:
        trs = []
        for prev, c in zip(candles[-15:-1], candles[-14:]):
            h, l, pc = _f(c["h"]), _f(c["l"]), _f(prev["c"])
            trs.append(max(h - l, abs(h - pc), abs(l - pc)))
        atr = sum(trs) / len(trs)
        out["atr14"] = round(atr, 4)
        out["atr14_pct"] = round(atr / closes[-1] * 100, 2)
    for w in (50, 200):
        if len(closes) >= w:
            ma = sum(closes[-w:]) / w
            out[f"ma{w}"] = round(ma, 4)
            out[f"vs_ma{w}_pct"] = round((closes[-1] / ma - 1) * 100, 2)
    return out


def fetch(ticker, dex="auto", n_candles=20):
    symbol = ALIASES.get(ticker.upper(), ticker.upper())
    dexes = list_dexes() if dex == "auto" else [dex]

    found = []
    for d in dexes:
        m = _market(d, symbol)
        if m:
            found.append((d, *m))
    if not found:
        return None  # 未上 HL

    def liquidity(item):
        _, _, ctx = item
        oi_ntl = (_f(ctx.get("openInterest")) or 0) * (_f(ctx.get("markPx")) or 0)
        return (_f(ctx.get("dayNtlVlm")) or 0, oi_ntl)

    found.sort(key=liquidity, reverse=True)
    best_dex, asset, ctx = found[0]
    coin = f"{best_dex}:{symbol}"

    funding_hr = _f(ctx.get("funding"))
    mark = _f(ctx.get("markPx"))
    oracle = _f(ctx.get("oraclePx"))
    prev = _f(ctx.get("prevDayPx"))
    now = dt.datetime.now(dt.timezone.utc)
    session = us_session(now)

    out = {
        "coin": coin,
        "ticker": ticker.upper(),
        "dex": best_dex,
        "mark": mark,
        "oracle": oracle,
        "mid": _f(ctx.get("midPx")),
        "prev_day": prev,
        "day_change_pct": round((mark / prev - 1) * 100, 2) if mark and prev else None,
        "mark_oracle_basis_pct": round((mark / oracle - 1) * 100, 3) if mark and oracle else None,
        "max_leverage": asset.get("maxLeverage"),
        "open_interest": _f(ctx.get("openInterest")),
        "day_ntl_vlm": _f(ctx.get("dayNtlVlm")),
        "funding_hourly": funding_hr,
        "funding_annual_pct": round(funding_hr * 24 * 365 * 100, 2) if funding_hr is not None else None,
        "fetched_at_utc": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "us_session": session,
        "source": f"Hyperliquid info API · {coin} · mark/oracle",
        "alternatives": [
            {
                "coin": f"{d}:{symbol}",
                "mark": _f(c.get("markPx")),
                "open_interest": _f(c.get("openInterest")),
                "stale": not (_f(c.get("openInterest")) or 0),
            }
            for d, _, c in found[1:]
        ],
    }
    caveats = []
    if not out["open_interest"]:
        caveats.append("该盘 OI=0，价格可能过期，勿作价格主源")
    if session != "regular":
        caveats.append("美股非常规交易时段：HL 价格不由现货连续驱动，结论前须用现货收盘交叉核对")
    if caveats:
        out["price_caveat"] = "；".join(caveats)

    if n_candles > 0:
        stats = _candle_stats(coin, n_candles)
        if stats:
            out["candles_1d"] = stats
    return out


def render(d):
    L = []
    L.append(f"# Hyperliquid 行情 · {d['coin']}（价格主源，无需 key）")
    L.append(f"  mark   ${d['mark']}    oracle ${d['oracle']}    mid ${d['mid']}    基差 {d['mark_oracle_basis_pct']}%")
    chg = d.get("day_change_pct")
    L.append(f"  前日收 ${d['prev_day']}   日内 {('+' if (chg or 0) >= 0 else '')}{chg}%")
    fa = d.get("funding_annual_pct")
    L.append(f"  资金费 {d['funding_hourly']}/小时 ≈ 年化 {fa}%（多头成本，短期杠杆须计）")
    L.append(f"  最大杠杆 {d['max_leverage']}x   未平仓 {d['open_interest']}   日成交额 ${d['day_ntl_vlm']}")
    c = d.get("candles_1d")
    if c:
        if c.get("n"):
            L.append(f"  近 {c['n']} 日线: 收 ${c['last_close']}  区间 ${c['range_low']}–${c['range_high']}")
        if c.get("atr14"):
            L.append(f"  ATR14 ${c['atr14']}（{c['atr14_pct']}%）")
        mas = [f"MA{w} ${c[f'ma{w}']}（偏离 {c[f'vs_ma{w}_pct']}%）" for w in (50, 200) if f"ma{w}" in c]
        if mas:
            L.append("  " + "  ".join(mas))
        else:
            L.append(f"  均线: 历史仅 {c['history_days']} 日，不足 MA50")
    L.append(f"  取数时间 {d['fetched_at_utc']}  美股时段: {d['us_session']}")
    if d.get("price_caveat"):
        L.append(f"  ⚠ {d['price_caveat']}")
    for alt in d.get("alternatives", []):
        flag = "（OI=0，价格过期勿用）" if alt["stale"] else ""
        L.append(f"  其他盘 {alt['coin']} mark ${alt['mark']}{flag}")
    L.append(f"  来源: {d['source']}")
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ticker")
    ap.add_argument("--dex", default="auto", help="auto=遍历所有 HIP-3 dex 选最活跃的盘")
    ap.add_argument("--candles", type=int, default=20)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    try:
        d = fetch(args.ticker, args.dex, args.candles)
    except (urllib.error.URLError, ValueError, KeyError, IndexError, TypeError) as e:
        print(f"取数失败: {e}", file=sys.stderr)
        sys.exit(2)

    if d is None:
        scope = "任何 dex" if args.dex == "auto" else f"{args.dex} dex"
        print(
            f"{args.ticker.upper()} 不在 Hyperliquid {scope} → 回退 WebSearch 取现货价。",
            file=sys.stderr,
        )
        sys.exit(3)

    print(json.dumps(d, ensure_ascii=False, indent=2) if args.json else render(d))


if __name__ == "__main__":
    main()
