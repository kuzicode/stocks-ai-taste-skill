---
last_updated: 2026-06-26
status: active
owner: kumata
---

# stocks-ai-taste-skill — 架构

本项目是一个自包含 Codex/Claude/OpenClaw/Hermes 可用的股票研究 skill。核心入口是 `SKILL.md`，执行时先做市场路由，再按市场加载对应知识文件、模板和校验器。

## 运行模型

无服务端、无数据库、无常驻进程。Agent 在仓库根目录读取文件、联网取数、运行 Python 脚本，并把报告写入本地运行期目录。

```text
用户请求
  -> SKILL.md 市场识别
  -> A 股路径 或 美股/海外路径
  -> 读取 knowledge/ 与 assets/
  -> 生成 reports/ 与 examples/
  -> 运行 scripts/ 校验
```

## 模块边界

| 模块 | 责任 |
|---|---|
| `SKILL.md` | skill 入口、市场识别、共性铁律、工作流路由 |
| `knowledge/frameworks/` | 美股/海外 AI 产业链分析框架、估值、偏差自检 |
| `knowledge/markets/` | A 股数据源、产业链路径、12 章研报工作流 |
| `assets/` | 人读报告模板 |
| `scripts/` | 可重复校验和行情辅助脚本 |
| `reports/` | 本地生成的人读报告，默认不入库 |
| `examples/` | 本地生成的结构化底稿，默认不入库 |

## 外部集成

- 美股/海外行情：`scripts/hl_price.py` 调 Hyperliquid 公开 info API；未覆盖时由 agent 联网回退现货价格。
- 美股/海外基本面：SEC filings、公司财报、电话会、机构目标价平台和权威财经来源。
- A 股数据：公司公告、交易所、巨潮资讯、东方财富、同花顺 thsdk/wencai、Wind/Choice/Tushare（可用则用）。

## 关键不变量

- 先识别市场，再加载对应路径；A 股不套 Hyperliquid 杠杆逻辑。
- 所有进入结论的数字必须在当次执行中核实并标明来源和日期。
- 报告结论必须区分长期配置与短期交易；两者可以不同。
- skill 不内置账号、访问令牌、外发频道 ID、私聊 ID 或代理地址。
- 不自动外发报告，除非用户在当次会话明确确认渠道、目标和凭据来源。

## 校验流

美股/海外：

```bash
python3 scripts/validate_thesis.py examples/<ticker>_<date>.yaml --as-of <date>
```

A 股：

```bash
python3 scripts/validate_a_share_report.py reports/<code_or_name>_<date>.md
```
