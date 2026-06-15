# ai-stock-analysis · AI 产业链股票分析 Skill

给定一只 AI 产业链个股 → **产业链定位 → 拉实时数据 → 4 维 thesis 判断 → 输出交易员视角研报**。
可在 **Claude Code / Codex / Hermes** 等主流 agent 对话中调用。

> ⚠️ 分析框架工具，**非投资建议**；数字以一手财报为准。

## 特性
- **产业链定位**：5 角色（上游设备/中游加速器/下游云/模型客户/电力支撑）× ~50 ticker × 护城河 × 卡点
- **4 维 thesis**（WHAT / WHY / SO WHAT / RISKS）+ Python 校验器机检（support 必带数字、red_flag 必带触发器、90 天内必有 catalyst）
- **估值 + 自检**：反向 DCF / 安全边际 + 5 心智模型 + 6 行为偏差 + 历史 base rate
- **双输出**：交易员速览（`reports/`，人读）+ 结构化底稿（`examples/`，机读）

## 判别力示例（同样"低 PE"，结论却相反）
| 标的 | 护城河 | 估值 | 判断 |
|---|---|---|---|
| NVDA | 强 (CUDA) | 便宜 23x | 🟢 买入 = 错杀 |
| MU | 弱 (周期) | 便宜 9x | ⚠️ 观望 = 周期顶陷阱 |
| MRVL | 中 (socket风险) | 贵 55-66x | 🟡 不追高 = 价格透支 |
| SPCX | 非 AI 链 | 极端 | ⚠️ 自动识别越界 → 通用模型速览 |

## 流程（7 步，详见 [`SKILL.md`](SKILL.md)）
```
输入 ticker
 → 0 一句话 thesis（写不出则停）
 → 1 industry_chain_map.yaml 定位
 → 2 拉实时数据（知识库仅 2025-26 快照，必须实时覆盖）
 → 3 填 4 维 thesis + 校验器机检
 → 4 估值 + 安全边际
 → 5 心智模型 + 偏差 + base rate
 → 6 输出交易员研报
```

## 安装
依赖：Python 3.8+ 与 `pyyaml`（仅校验器需要，`pip install pyyaml`）；agent 需具备联网搜索能力（Step 2）。

| Agent | 安装 / 调用 |
|---|---|
| **Claude Code** | `git clone <repo> ~/.claude/skills/ai-stock-analysis` → 对话说「分析 NVDA」或 `/ai-stock-analysis`（靠 SKILL.md frontmatter 自动匹配） |
| **Codex** | `git clone <repo> && cd` → 运行 `codex` → 读 `AGENTS.md`「运行方式」驱动 |
| **Hermes / 通用** | 把 `SKILL.md` 载入上下文 + 给文件读取&联网工具 + 工作目录设为仓库根 |

## 使用
```
分析 NVDA                  # 默认：先交易员速览，再附结构化底稿
分析 MU report=trader      # 只要人读研报
分析 ASML report=structured # 只要 4 维 thesis YAML
分析 TSM mode=quick        # 精简版
```
- 人读研报 → `reports/<TICKER>_<日期>.md`（格式见 [`assets/trader_report_template.md`](assets/trader_report_template.md)）
- 结构化底稿 → `examples/<ticker>_<日期>.yaml`，校验：`python3 scripts/validate_thesis.py <底稿> --as-of <日期>`
- 非 AI 链标的（如 SPCX=SpaceX）自动改用通用投资模型 + 显著免责，不强套 AI 框架

> `reports/` 与 `examples/` 为运行期输出目录，内容默认不入库（见 `.gitignore`），克隆下来是空的。

## 结构
```
SKILL.md              skill 主体（7 步 + I/O 契约）
AGENTS.md / CLAUDE.md 各 agent harness 入口
assets/               交易员研报模板
scripts/              4 维 thesis 校验器
knowledge/frameworks/ ★ 原创综合资产（产业链地图 / thesis 模板 / 估值 / 心智模型 / SOP）
docs/skill_design.md  设计依据
```

## 时效 · 免责 · 版权
- 知识库内容截至原文 **2025-26**，均为快照；skill 在 Step 2 **强制拉实时数据**覆盖。
- 仅作分析框架演示，**不构成投资建议**，决策与风险自负。
- `knowledge/frameworks/` 为本项目**原创综合**；方法论概念源自 wizzai101.com，其逐章精读笔记出于版权考虑**默认不公开分发**（`.gitignore` 已屏蔽）。
- 仓库未预置 `LICENSE`，请按需自选。
