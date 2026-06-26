#!/usr/bin/env python3
"""A 股 Markdown 研报校验器。

用法:
    python3 scripts/validate_a_share_report.py "reports/<日期> - <中文简称 代号> - A-share.md"
    （文件名含空格，需整体加引号）

校验范围:
    1. 12 个深度报告章节齐全
    2. 估值章节包含 WACC/FCF/DCF/DDM/PE/PB/PEG/杜邦
    3. 包含产业链路径、价值捕获评分、长期配置价值、短期交易窗口
    4. 包含数据核实日期和主要来源
    5. 不包含常见隐私/外发配置字段

退出码:
    0 = 通过, 1 = 校验失败, 2 = 用法/读取错误。
"""
import argparse
import re
import sys
from pathlib import Path


REQUIRED_SECTIONS = [
    "1. 公司概况",
    "2. 五年经营业绩",
    "3. 客户结构",
    "4. 股东结构",
    "5. 管理团队",
    "6. 行业格局",
    "7. 研发与 CAPEX 投向",
    "8. 风险分析",
    "9. 多维度估值",
    "10. 竞争对手深度对比",
    "11. 技术分析与操作指引",
    "12. 综合结论",
]

VALUATION_TERMS = [
    "WACC",
    "Ke",
    "Kd",
    "FCF",
    "ROE",
    "留存率",
    "DCF",
    "DDM",
    "PE",
    "PB",
    "PEG",
    "杜邦",
]

CORE_TERMS = [
    "产业链路径",
    "上游",
    "下游",
    "价值捕获",
    "长期",
    "配置价值",
    "短期",
    "交易",
    "止损",
    "止盈",
    "数据核实日期",
    "主要来源",
]

SENSITIVE_PATTERNS = [
    (re.compile(r"\bchat_id\b", re.I), "chat_id"),
    (re.compile(r"\bthread_id\b", re.I), "thread_id"),
    (re.compile(r"\bbot[_ -]?token\b", re.I), "bot token"),
    (re.compile(r"\btgID\b", re.I), "tgID"),
    (re.compile(r"127\.0\.0\.1:7890"), "local proxy"),
    (re.compile(r"(?<!\d)1[3-9]\d{9}(?!\d)"), "11 位手机号"),
    (re.compile(r"\b\d{8,}:[A-Za-z0-9_-]{20,}\b"), "Telegram token-like string"),
]


def has_section(text, title):
    pattern = re.compile(rf"^##\s+{re.escape(title)}\b", re.M)
    return bool(pattern.search(text))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("path")
    args = parser.parse_args()

    path = Path(args.path)
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"读取失败: {exc}", file=sys.stderr)
        return 2

    errors = []

    for section in REQUIRED_SECTIONS:
        if not has_section(text, section):
            errors.append(f"缺少章节: {section}")

    for term in VALUATION_TERMS:
        if term not in text:
            errors.append(f"估值硬项缺失: {term}")

    for term in CORE_TERMS:
        if term not in text:
            errors.append(f"核心内容缺失: {term}")

    for pattern, label in SENSITIVE_PATTERNS:
        if pattern.search(text):
            errors.append(f"疑似隐私/外发配置泄露: {label}")

    if errors:
        print(f"✗ {path} 校验未通过（{len(errors)} 项）:")
        for err in errors:
            print(f"    - {err}")
        return 1

    print(f"✓ {path} 通过 A 股研报结构校验")
    return 0


if __name__ == "__main__":
    sys.exit(main())
