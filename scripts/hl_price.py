#!/usr/bin/env python3
"""Hyperliquid 美股 perp 价格取数 — skill 的价格主源（无需 API key）。

用法:
    python3 scripts/hl_price.py NVDA              # 人类可读速览
    python3 scripts/hl_price.py NVDA --json       # 机读 JSON
    python3 scripts/hl_price.py NVDA --candles 20 # 附最近 N 日线高低/区间（默认 20）
    python3 scripts/hl_price.py NVDA --dex xyz     # 指定 perp dex（默认 xyz）

数据源: POST https://api.hyperliquid.xyz/info（公开，无需 key）
    - metaAndAssetCtxs(dex=xyz): markPx / oraclePx / midPx / funding / maxLeverage / OI / prevDayPx
    - candleSnapshot(coin=xyz:<T>, interval=1d): 日线 OHLCV → 近 N 日高低区间

美股 perp 命名: dex=`xyz`，币种 `xyz:<TICKER>`（如 xyz:NVDA / xyz:CRWV / xyz:SPCX）。
funding 为 Hyperliquid **每小时**资金费率；年化 = funding × 24 × 365。

退出码:
    0 = 成功
    3 = 该 ticker 不在 Hyperliquid <dex> 列表 → 调用方应回退 WebSearch 取现货价
    2 = 网络/解析错误或用法错误
"""
import argparse
import json
import sys
import urllib.error
import urllib.request

API = "https://api.hyperliquid.xyz/info"
HOUR_MS = 3600 * 1000


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


def fetch(ticker, dex, n_candles):
    coin = f"{dex}:{ticker.upper()}"

    meta, ctxs = _post({"type": "metaAndAssetCtxs", "dex": dex})
    universe = meta.get("universe", [])
    idx = next((i for i, a in enumerate(universe) if a.get("name") == coin), None)
    if idx is None:
        return None  # 未上 HL

    asset = universe[idx]
    ctx = ctxs[idx]
    funding_hr = _f(ctx.get("funding"))
    mark = _f(ctx.get("markPx"))
    prev = _f(ctx.get("prevDayPx"))

    out = {
        "coin": coin,
        "ticker": ticker.upper(),
        "dex": dex,
        "mark": mark,
        "oracle": _f(ctx.get("oraclePx")),
        "mid": _f(ctx.get("midPx")),
        "prev_day": prev,
        "day_change_pct": round((mark / prev - 1) * 100, 2) if mark and prev else None,
        "max_leverage": asset.get("maxLeverage"),
        "open_interest": _f(ctx.get("openInterest")),
        "day_ntl_vlm": _f(ctx.get("dayNtlVlm")),
        "funding_hourly": funding_hr,
        "funding_annual_pct": round(funding_hr * 24 * 365 * 100, 2) if funding_hr is not None else None,
        "source": f"Hyperliquid info API · {coin} · mark/oracle",
    }

    # 当前时间从最新日线推断（脚本内禁用 wall-clock 以保持可复现），用足够大的窗口取末段
    if n_candles > 0:
        # endTime 取一个很大的未来值，HL 会裁剪到最新；startTime 回溯 n+5 个交易日
        end = 4102444800000  # 2100-01-01，远大于现在 → 取到最新
        start = end - (n_candles + 10) * 86400 * 1000
        candles = _post({"type": "candleSnapshot", "req": {
            "coin": coin, "interval": "1d", "startTime": start, "endTime": end}})
        candles = candles[-n_candles:] if candles else []
        if candles:
            highs = [_f(c["h"]) for c in candles]
            lows = [_f(c["l"]) for c in candles]
            out["candles_1d"] = {
                "n": len(candles),
                "last_close": _f(candles[-1]["c"]),
                "range_high": max(highs),
                "range_low": min(lows),
                "first_open": _f(candles[0]["o"]),
            }
    return out


def render(d):
    L = []
    L.append(f"# Hyperliquid 行情 · {d['coin']}（价格主源，无需 key）")
    L.append(f"  mark   ${d['mark']}    oracle ${d['oracle']}    mid ${d['mid']}")
    chg = d.get("day_change_pct")
    L.append(f"  前日收 ${d['prev_day']}   日内 {('+' if (chg or 0) >= 0 else '')}{chg}%")
    fa = d.get("funding_annual_pct")
    L.append(f"  资金费 {d['funding_hourly']}/小时 ≈ 年化 {fa}%（多头成本，短期杠杆须计）")
    L.append(f"  最大杠杆 {d['max_leverage']}x   未平仓 {d['open_interest']}   日成交额 ${d['day_ntl_vlm']}")
    c = d.get("candles_1d")
    if c:
        L.append(f"  近 {c['n']} 日线: 收 ${c['last_close']}  区间 ${c['range_low']}–${c['range_high']}")
    L.append(f"  来源: {d['source']}")
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ticker")
    ap.add_argument("--dex", default="xyz")
    ap.add_argument("--candles", type=int, default=20)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    try:
        d = fetch(args.ticker, args.dex, args.candles)
    except (urllib.error.URLError, ValueError, KeyError, IndexError) as e:
        print(f"取数失败: {e}", file=sys.stderr)
        sys.exit(2)

    if d is None:
        print(
            f"{args.ticker.upper()} 不在 Hyperliquid {args.dex} 列表 → 回退 WebSearch 取现货价。",
            file=sys.stderr,
        )
        sys.exit(3)

    print(json.dumps(d, ensure_ascii=False, indent=2) if args.json else render(d))


if __name__ == "__main__":
    main()
