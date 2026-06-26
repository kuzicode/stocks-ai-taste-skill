# ai-stock-analysis

统一股票研究 skill：给定股票代码、公司名或行业主题，先识别市场，再走对应分析路径。

- **美股/海外**：AI 产业链定位、实时行情、4 维 thesis、估值、安全边际、长期正股与短期 Hyperliquid 交易判断。
- **A 股**：最新数据源、产业链路径、12 章深度研报、DCF/DDM/杜邦估值、长期配置与短期交易判断。

> 仅作研究框架与信息整理，不构成投资建议。进入结论的数字必须以本次核实的一手来源为准。

## 快速使用

```text
分析 NVDA
分析 MU report=trader
分析 ASML mode=quick
分析 盛美上海
分析 688981
分析 半导体设备 A 股对比
```

默认输出：

- 美股/海外报告：`reports/<TICKER>_<YYYY-MM-DD>.md`
- 美股/海外结构化底稿：`examples/<ticker>_<YYYY-MM-DD>.yaml`
- A 股报告：`reports/<代码或公司>_<YYYY-MM-DD>.md`

`reports/` 和 `examples/` 是运行期产物，默认不入库。

## 市场分流

`SKILL.md` 先判断市场：

- A 股代码或中文 A 股公司名 → 读取 `knowledge/markets/a_share_workflow.md`
- 美股/海外 ticker 或公司名 → 读取 `knowledge/frameworks/analysis_checklist.md`
- 不确定市场 → 先问用户确认，不猜

A 股不使用 Hyperliquid 合约逻辑；美股/海外继续优先使用 `scripts/hl_price.py` 获取 Hyperliquid 美股 perp 行情，未覆盖时回退现货价格。

## 核心文件

```text
SKILL.md                         # 统一入口与市场路由
AGENTS.md                        # agent 协作规则
assets/
  trader_report_template.md      # 美股/海外交易员速览模板
  a_share_report_template.md     # A 股 12 章 Markdown 模板
knowledge/frameworks/            # 美股/海外 AI 产业链框架
knowledge/markets/               # A 股流程、数据源、产业链路径
scripts/
  hl_price.py                    # Hyperliquid 美股 perp 行情
  validate_thesis.py             # 美股/海外 4 维 thesis 校验
  validate_a_share_report.py     # A 股研报结构校验
```

## 安装

把本仓库放到对应 agent 的 skills 目录，或直接在仓库根目录运行 agent。

```bash
git clone <repo> ~/.codex/skills/ai-stock-analysis
git clone <repo> ~/.claude/skills/ai-stock-analysis
git clone <repo> ~/.openclaw/skills/ai-stock-analysis
```

运行环境建议：

- Python 3.8+
- A 股校验器只依赖标准库
- `validate_thesis.py` 需要 PyYAML
- agent 需要文件读写、Shell、联网检索/抓取能力

## 验证

```bash
python3 scripts/validate_thesis.py examples/<ticker>_<date>.yaml --as-of <date>
python3 scripts/validate_a_share_report.py reports/<code_or_name>_<date>.md
```

A 股报告校验会检查：

- 12 个章节是否齐全
- WACC、FCF、DCF、DDM、PE/PB/PEG、杜邦是否出现
- 产业链路径、长期配置、短期交易、止损止盈是否出现
- 数据核实日期和主要来源是否出现
- 是否疑似泄露手机号、访问令牌、外发频道 ID、代理地址等敏感配置

## 数据与隐私

- 所有报告必须标明数据核实日期和主要来源。
- skill 不内置账号、访问令牌、外发频道 ID、私聊 ID 或代理地址。
- 不自动发送报告到外部渠道；如需外发，必须由用户在当次会话明确确认。

## 版权与边界

`knowledge/frameworks/` 为项目整理的研究框架；逐章精读笔记和运行期报告默认不公开分发。仓库未预置 `LICENSE`，发布前请按需补充。
