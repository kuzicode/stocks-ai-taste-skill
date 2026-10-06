---
last_updated: 2026-10-06
status: active
owner: kumata
---

# stocks-ai-taste-skill — 实施计划历史归档

本文件保存从 `docs/plan.md` 迁出的已完成或废弃计划。新会话默认不读此文件；只有追溯历史决策时再打开。

活跃计划见 `docs/plan.md`。

---

<!--
迁入格式：

## M1 — <里程碑名称>（完成日期）

<从 docs/plan.md 迁出的原始计划内容>
-->

## M1-M4 — 知识库 → SKILL.md → HL 价格主源/双角度 → A 股/港股路由（完成 2026-06-26，2026-10-06 归档）

### 问题 / 目标
做一个「AI 产业链股票分析并判断投资逻辑」的 skill。当前为**准备阶段**：先建知识框架库 + 技能设计文档，不急于实现 skill。

### 方案
精读 wizzai101.com Part1（产业 C1-C10）+ Part2（投资 P2A 通用 / P2B AI 特有）共 20 篇，沉淀为：
1. 20 篇逐章笔记（统一模板）
2. 5 份跨章综合框架（2 YAML 结构化 + 3 md）
3. 1 份技能设计蓝图

### 影响文件
- `knowledge/part1_industry/*.md`（10）、`knowledge/part2a_general/*.md`（5）、`knowledge/part2b_ai_specific/*.md`（5）
- `knowledge/frameworks/{industry_chain_map.yaml, thesis_4dim_template.yaml, valuation_toolkit.md, mental_models_and_biases.md, analysis_checklist.md}`
- `knowledge/README.md`、`docs/skill_design.md`、`AGENTS.md`、`CLAUDE.md`

### 验收 checklist
- [x] 20 篇逐章笔记齐全（每篇 source + read_date + 模板五段）
- [x] industry_chain_map.yaml 覆盖 5 角色、≥52 ticker，可解析
- [x] thesis_4dim_template.yaml 字段对齐 P2B-C2（4 维 + 自检规则），可解析
- [x] 5 份 frameworks + README + skill_design 完成
- [x] 干跑：仅用知识库对 NVDA 走一遍 analysis_checklist，产出填好的 4 维 thesis（库自洽，唯一缺口=实时数据）
- [x] 两个 YAML 通过解析校验（safe_load_all 通过；chain_map 45 条目覆盖全 5 角色）

### 阶段 2 — 实现 SKILL.md（已完成）
按 `docs/skill_design.md` 实现可运行 skill。
- 影响文件：`SKILL.md`（根，skill 主体）、`scripts/validate_thesis.py`（4 维 thesis 校验器）
- 验收：
  - [x] SKILL.md 含 7 步流程 + I/O 契约 + 引用 knowledge/frameworks 相对路径
  - [x] validate_thesis.py 实现 5 项硬校验（view 单点 / support 含数字 / red_flag 含 trigger / 90 天 catalyst 约束 / price_outlook 锚定）
  - [x] 校验器在 thesis_4dim_template.yaml 的 NVDA 范例上通过；对残缺 thesis 报错
- 后续：实时取数层接入；用 NVDA/ASML/CRWV 做端到端回归（未启动）。

### 阶段 3 — 输出优化：价格主源 + 机构目标价 + 双角度结论（已完成）

#### 问题 / 目标
1. **价格主源切到 Hyperliquid**：调取行情优先用 Hyperliquid 美股 perp（dex=`xyz`，符号 `xyz:<TICKER>`），主源 = `markPx`/`oraclePx` + 日线 `candleSnapshot`，无需 API key；不在列表才回退 WebSearch 现货价。
2. **增加机构评估预估价格参考**：输出里显式给分析师/机构目标价（高/中/低 + 家数 + 来源），与自算 fair_value_range 并列做交叉锚。
3. **结论分短期 / 长期两个角度**：
   - **长期** = 股票账户正股长期持有（buy/hold/sell + 仓位 + 安全边际加仓区）。
   - **短期** = Hyperliquid 合约杠杆操作（方向 + 杠杆区间≤maxLev + 入场/止损/止盈 + 资金费成本 + 触发条件）。

#### 方案
- 新增 `scripts/hl_price.py`：封装 Hyperliquid info API，输出 mark/oracle/mid/funding(时/年化)/maxLev/OI + 近 N 日线高低区间；退出码 3=未上 HL→回退。
- `SKILL.md`：Step2 增「价格主源=HL + 机构目标价必拉」；Step4 增机构目标价锚；Step6 拆双角度；输出契约加 `analyst_targets` + `decision.long_term`/`decision.short_term`。
- `thesis_4dim_template.yaml`：`price_outlook` 下加 `analyst_targets`（附加字段，不破坏 5 项校验）。
- `assets/trader_report_template.md`：结论拆「🎯 长期(正股) / ⚡ 短期(HL 杠杆)」两块 + 机构参考价行 + 更新渲染规则与 MU 范例。
- `docs/skill_design.md`：补数据源优先级 + 双角度输出契约。
- `examples/nvda_*.yaml`：补 `analyst_targets` 作参考（仍过校验）。

#### 影响文件
- 新增 `scripts/hl_price.py`
- 改 `SKILL.md`、`knowledge/frameworks/thesis_4dim_template.yaml`、`assets/trader_report_template.md`、`docs/skill_design.md`、`examples/nvda_2026-06-15.yaml`

#### 验收 checklist
- [x] `hl_price.py NVDA` 返回 mark/oracle/funding/maxLev + 日线区间；未上 HL 的 ticker 退出码 3（NVDA 20x / CRWV 10x / ZZZZ exit3 实测通过）
- [x] SKILL Step2/4/6 + 输出契约含 HL 主源、机构目标价、双角度结论
- [x] thesis 模板加 analyst_targets 后 `validate_thesis.py` 仍通过 NVDA 范例
- [x] trader 模板含长/短两块 + 机构参考价，MU 范例已重渲染
- [x] examples/nvda 补 analyst_targets + 双角度 decision 后仍过校验
- [x] AGENTS.md / README / skill_design 同步更新；无残留旧名

### 阶段 4 — 市场路由：整合 A 股研报工作流（已完成）

#### 问题 / 目标
把现有 `ai-stock-analysis` 从单一美股/海外 AI 产业链分析，扩展为统一股票研究入口：
1. 先识别标的是 A 股还是美股/海外市场；
2. 美股/海外继续走现有 AI 产业链 + HL 价格源 + 4 维 thesis 工作流；
3. A 股走独立数据源、12 章深度研报、估值三件套与长期/短期双视角；
4. A 股报告默认生成 Markdown 到 `reports/`，不内置账号、访问令牌、外发频道 ID 或自动发送逻辑。

#### 方案
- `SKILL.md`：增加市场识别与分流，A 股路径按需读取 `knowledge/markets/a_share_workflow.md`。
- 新增 `knowledge/markets/a_share_workflow.md`：A 股 6 步流程、12 章结构、估值硬约束、长期/短期结论。
- 新增 `knowledge/markets/a_share_data_sources.md`：同花顺/巨潮/交易所/东方财富/财报等最新数据源优先级。
- 新增 `knowledge/markets/a_share_industry_chain_map.yaml`：A 股产业链路径分析框架与关注标的。
- 新增 `assets/a_share_report_template.md`：A 股 Markdown 研报模板。
- 新增 `scripts/validate_a_share_report.py`：检查 12 章、估值三件套、产业链路径、长期/短期结论、来源日期和隐私泄露关键词。

#### 影响文件
- 改 `SKILL.md`、`AGENTS.md`、`docs/plan.md`
- 新增 `knowledge/markets/{a_share_workflow.md,a_share_data_sources.md,a_share_industry_chain_map.yaml}`
- 新增 `assets/a_share_report_template.md`
- 新增 `scripts/validate_a_share_report.py`

#### 验收 checklist
- [x] `SKILL.md` 能清晰路由 A 股 vs 美股/海外，且美股路径不降级
- [x] A 股 workflow 强制最新数据、产业链路径、12 章、估值三件套、长期/短期建议
- [x] A 股报告默认写到 `reports/<code_or_name>_<as_of_date>.md`
- [x] A 股 skill 内容不包含手机号、TG token 值、外发频道 ID 值、代理地址等敏感交付信息
- [x] `validate_a_share_report.py` 可运行并能识别缺失章节/隐私泄露
- [x] `quick_validate.py` 因当前 Python 环境缺 PyYAML 未能直接运行；已用 Ruby YAML 等价校验 `SKILL.md` frontmatter 仅含 name/description

