#!/usr/bin/env python3
"""4 维 thesis 校验器 — 操作化 P2B-C2 的 5 项完成自检。

用法:
    python3 scripts/validate_thesis.py <thesis.yaml> [--as-of YYYY-MM-DD]

as-of 取值优先级: --as-of > thesis 的 as_of_date 字段 > 文件头注释 `as_of_date: YYYY-MM-DD`（旧底稿兼容，告警）> 今天（告警）。
这样旧 thesis 无论何时重跑都按其分析日期校验，不会随今天漂移。

校验规则（全部通过才算合格）:
    1. view 是明确单点立场 (bull/bear/neutral/watching)，且 confidence ∈ {high,medium,low}
    2. 每条 support 含数字（数据点须可证伪）
    3. 每条 red_flag 含非空 trigger
    4. 90 天内至少有一个 catalyst；否则 confidence 必须 low 或 view=watching（硬约束）
    5. price_outlook 含 current 且至少 base_90d（锚定当前价）
    6. （存在 decision.short_term 时）杠杆上限 ≤ hl_market.max_leverage
    7. （存在 decision.short_term 且方向为多/空时）止损在入场区正确一侧（多: 止损 < 入场下沿；空: 止损 > 入场上沿）

退出码: 0 = 通过, 1 = 校验失败, 2 = 用法/解析错误。
依赖: PyYAML。多文档 YAML 中跳过仍含占位符 `___` 的模板块，只校验已填写的 thesis。
"""
import argparse
import datetime as dt
import re
import sys

try:
    import yaml
except ImportError:
    print("需要 PyYAML：pip install pyyaml", file=sys.stderr)
    sys.exit(2)

VIEWS = {"bull", "bear", "neutral", "watching"}
CONFIDENCES = {"high", "medium", "low"}
DATE_RE = re.compile(r"\d{4}-\d{2}-\d{2}")
NUM_RE = re.compile(r"\d")
HEADER_ASOF_RE = re.compile(r"as_of_date:\s*(\d{4}-\d{2}-\d{2})")
PAREN_RE = re.compile(r"[（(][^）)]*[）)]")
LEV_RE = re.compile(r"(\d+(?:\.\d+)?)\s*[x×]", re.I)
DOLLAR_RE = re.compile(r"\$\s*([\d,]+(?:\.\d+)?)")
PLAIN_NUM_RE = re.compile(r"(?<![\d.])([\d,]+(?:\.\d+)?)(?!\s*[x×%\d])")


def parse_date(value):
    """接受 date 对象或 YYYY-MM-DD 字符串，取不出则返回 None。"""
    if isinstance(value, dt.date):
        return value
    if isinstance(value, str):
        m = DATE_RE.search(value)
        if m:
            try:
                return dt.date.fromisoformat(m.group(0))
            except ValueError:
                return None
    return None


def _strip_paren(value):
    return PAREN_RE.sub("", str(value))


def max_leverage_of(value):
    """'2-3x' → 3；'1-2x（≤10x上限）' → 2（括号内说明不计）；取不出返回 None。"""
    nums = [float(n) for n in LEV_RE.findall(_strip_paren(value))]
    if not nums:
        nums = [float(n) for n in LEV_RE.findall(str(value))]
    return max(nums) if nums else None


def prices_of(value):
    """抽取价格数字：优先 $ 前缀，否则取普通数字（排除杠杆 x / 百分比）。"""
    text = _strip_paren(value)
    found = DOLLAR_RE.findall(text) or PLAIN_NUM_RE.findall(text)
    out = []
    for n in found:
        try:
            out.append(float(n.replace(",", "")))
        except ValueError:
            pass
    return out


def direction_of(value):
    text = str(value).lower()
    if "short" in text or "做空" in text or "空单" in text:
        return "short"
    if "long" in text or "做多" in text or "多单" in text:
        return "long"
    return None  # 观望 / 未指明 → 不做止损方向检查


def find_block(doc, key):
    """decision / hl_market 可能在顶层，也可能在 _analysis 下。"""
    if isinstance(doc.get(key), dict):
        return doc[key]
    analysis = doc.get("_analysis")
    if isinstance(analysis, dict) and isinstance(analysis.get(key), dict):
        return analysis[key]
    return {}


def validate_short_term(doc):
    errs = []
    st = find_block(doc, "decision").get("short_term")
    if not isinstance(st, dict):
        return errs

    # 规则 6：杠杆 ≤ maxLev
    max_lev = max_leverage_of(find_block(doc, "hl_market").get("max_leverage", ""))
    lev = max_leverage_of(st.get("leverage", ""))
    if lev is not None and max_lev is not None and lev > max_lev:
        errs.append(f"[DECISION] short_term 杠杆 {lev:g}x 超过 HL 最大杠杆 {max_lev:g}x")

    # 规则 7：止损方向
    side = direction_of(st.get("direction", ""))
    entry = prices_of(st.get("entry", ""))
    stop = prices_of(st.get("stop_loss", ""))
    if side and entry and stop:
        if side == "long" and not max(stop) < min(entry):
            errs.append(f"[DECISION] 做多止损 {stop} 应低于入场下沿 {min(entry):g}")
        if side == "short" and not min(stop) > max(entry):
            errs.append(f"[DECISION] 做空止损 {stop} 应高于入场上沿 {max(entry):g}")
    return errs


def resolve_as_of(doc, cli_as_of, header_as_of):
    """返回 (as_of, 告警或 None)。"""
    if cli_as_of:
        return cli_as_of, None
    d = parse_date(doc.get("as_of_date"))
    if d:
        return d, None
    if header_as_of:
        return header_as_of, "缺 as_of_date 字段，暂用文件头注释日期；请补字段"
    return dt.date.today(), "缺 as_of_date 字段，按今天校验（旧 thesis 可能误报 catalyst 缺失）"


def validate(doc, as_of):
    """返回错误列表；空列表表示通过。"""
    errs = []
    t = doc.get("ticker", "?")

    # 规则 1：view + confidence
    view = str(doc.get("view", "")).strip().lower()
    conf = str(doc.get("confidence", "")).strip().lower()
    if view not in VIEWS:
        errs.append(f"[WHAT] view 必须是 {sorted(VIEWS)} 之一，当前: {doc.get('view')!r}")
    if conf not in CONFIDENCES:
        errs.append(f"[WHY] confidence 必须是 {sorted(CONFIDENCES)} 之一，当前: {doc.get('confidence')!r}")

    # 规则 2：supports 含数字
    supports = doc.get("supports") or []
    if len(supports) < 3:
        errs.append(f"[WHAT] supports 至少 3 条，当前 {len(supports)} 条")
    for i, s in enumerate(supports, 1):
        if not NUM_RE.search(str(s)):
            errs.append(f"[WHAT] support#{i} 缺数字（须带可证伪数据点）: {s!r}")

    # 规则 3：red_flags 含 trigger
    red_flags = doc.get("red_flags") or []
    if not red_flags:
        errs.append("[RISKS] 至少 1 条 red_flag")
    for i, rf in enumerate(red_flags, 1):
        trig = (rf or {}).get("trigger") if isinstance(rf, dict) else None
        if not trig or not str(trig).strip():
            errs.append(f"[RISKS] red_flag#{i} 缺可观察 trigger")

    # 规则 4：90 天 catalyst 硬约束
    catalysts = doc.get("catalysts_90d") or []
    horizon = as_of + dt.timedelta(days=90)
    in_window = []
    for c in catalysts:
        d = parse_date((c or {}).get("date")) if isinstance(c, dict) else None
        if d and as_of <= d <= horizon:
            in_window.append(d)
    if not in_window:
        if not (conf == "low" or view == "watching"):
            errs.append(
                f"[SO WHAT] {as_of}~{horizon} 内无 catalyst → confidence 必须 low 或 view=watching"
                f"（当前 view={view!r}, confidence={conf!r}）"
            )

    # 规则 5：price_outlook 锚定
    po = doc.get("price_outlook") or {}
    if not po.get("current"):
        errs.append("[SO WHAT] price_outlook.current 缺失（须锚定当前价）")
    if not po.get("base_90d"):
        errs.append("[SO WHAT] price_outlook.base_90d 缺失")

    # 规则 6-7：短期决策机检
    errs.extend(validate_short_term(doc))

    return t, errs


def is_filled(doc):
    """跳过仍含占位符的模板块。"""
    if not isinstance(doc, dict) or "ticker" not in doc:
        return False
    return "___" not in yaml.safe_dump(doc, allow_unicode=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path")
    ap.add_argument("--as-of", default=None, help="覆盖 thesis 的 as_of_date（默认读文件）")
    args = ap.parse_args()

    cli_as_of = None
    if args.as_of:
        try:
            cli_as_of = dt.date.fromisoformat(args.as_of)
        except ValueError:
            print(f"--as-of 格式应为 YYYY-MM-DD，当前: {args.as_of!r}", file=sys.stderr)
            sys.exit(2)

    try:
        with open(args.path, encoding="utf-8") as f:
            raw = f.read()
        docs = list(yaml.safe_load_all(raw))
    except (OSError, yaml.YAMLError) as e:
        print(f"读取/解析失败: {e}", file=sys.stderr)
        sys.exit(2)

    filled = [d for d in docs if is_filled(d)]
    if not filled:
        print("未找到已填写的 thesis（所有文档仍含占位符 ___ 或无 ticker）。", file=sys.stderr)
        sys.exit(2)

    m = HEADER_ASOF_RE.search(raw)
    header_as_of = parse_date(m.group(1)) if m else None

    ok = True
    for doc in filled:
        as_of, warn = resolve_as_of(doc, cli_as_of, header_as_of)
        if warn:
            print(f"⚠ {doc.get('ticker', '?')}: {warn}", file=sys.stderr)
        ticker, errs = validate(doc, as_of)
        if errs:
            ok = False
            print(f"✗ {ticker} 校验未通过（{len(errs)} 项）:")
            for e in errs:
                print(f"    - {e}")
        else:
            print(f"✓ {ticker} 通过自检（as-of {as_of}）")

    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
