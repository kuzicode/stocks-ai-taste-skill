#!/usr/bin/env python3
"""4 维 thesis 校验器 — 操作化 P2B-C2 的 5 项完成自检。

用法:
    python3 scripts/validate_thesis.py <thesis.yaml> [--as-of YYYY-MM-DD]

校验规则（全部通过才算合格）:
    1. view 是明确单点立场 (bull/bear/neutral/watching)，且 confidence ∈ {high,medium,low}
    2. 每条 support 含数字（数据点须可证伪）
    3. 每条 red_flag 含非空 trigger
    4. 90 天内至少有一个 catalyst；否则 confidence 必须 low 或 view=watching（硬约束）
    5. price_outlook 含 current 且至少 base_90d（锚定当前价）

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

    return t, errs


def is_filled(doc):
    """跳过仍含占位符的模板块。"""
    if not isinstance(doc, dict) or "ticker" not in doc:
        return False
    return "___" not in yaml.safe_dump(doc, allow_unicode=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path")
    ap.add_argument("--as-of", default=dt.date.today().isoformat())
    args = ap.parse_args()

    try:
        as_of = dt.date.fromisoformat(args.as_of)
    except ValueError:
        print(f"--as-of 格式应为 YYYY-MM-DD，当前: {args.as_of!r}", file=sys.stderr)
        sys.exit(2)

    try:
        with open(args.path, encoding="utf-8") as f:
            docs = list(yaml.safe_load_all(f))
    except (OSError, yaml.YAMLError) as e:
        print(f"读取/解析失败: {e}", file=sys.stderr)
        sys.exit(2)

    filled = [d for d in docs if is_filled(d)]
    if not filled:
        print("未找到已填写的 thesis（所有文档仍含占位符 ___ 或无 ticker）。", file=sys.stderr)
        sys.exit(2)

    ok = True
    for doc in filled:
        ticker, errs = validate(doc, as_of)
        if errs:
            ok = False
            print(f"✗ {ticker} 校验未通过（{len(errs)} 项）:")
            for e in errs:
                print(f"    - {e}")
        else:
            print(f"✓ {ticker} 通过 5 项自检（as-of {as_of}）")

    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
