---
name: ai-stock-analysis
description: >
  分析 AI 产业链个股并输出投资判断。当用户要求分析/研究一只 AI 相关股票或板块
  （如「分析 NVDA」「看看光模块」「ASML 现在能买吗」「评估 CoreWeave 风险」），
  或要为某 AI 标的写投资 thesis、判断买/持/卖、做产业链定位与估值时使用。
  流程：产业链定位 → 拉实时数据 → 填 4 维 thesis → 估值+安全边际 → 心智模型/偏差交叉验证 → 输出结构化判断。
allowed-tools: Read, WebSearch, WebFetch, Bash, Write
---

# AI 产业链股票分析 skill

把一只 AI 产业链个股转成一份**可执行、可证伪、可季度复盘**的投资判断。
方法论与数据底座全部在本 skill 同目录的 `knowledge/`，**执行时按需 Read 加载**，不要凭记忆编造数字。

## 输入
`{ target: <ticker/公司名/主题>, as_of_date: <YYYY-MM-DD，默认今天>, mode: full | quick, report: both | trader | structured }`
- `mode`：`full`（默认）跑完整 7 步；`quick` 只做 Step 0/1/3 精简版 + 结论，跳过深度估值。
- `report`：输出渲染（默认 `both`）。`structured`=只出契约 YAML；`trader`=只出交易员速览；`both`=先速览后契约。
  用户说「给交易员看 / 通俗 / 简单报告」时用 `trader`。

## 铁律（先读）
1. **数据时效**：`knowledge/` 知识截至原文 2025-26，其中所有财务数字均为**快照/估算**。凡进入结论的具体数字，必须在 Step 2 用 WebSearch/最新财报**重新核实**；不可直接引用知识库数值。输出必须带 `data_freshness_note`。
2. **4 维不缺一维**：thesis 缺哪维就在哪破。Step 3 的 5 项自检必须全过（用校验器机检）。
3. **先 WHAT 后 WHY**：写不出 ≤30 字的一句话 thesis 就停，不强行建仓。
4. **方法 vs 事实**：`knowledge/part2b_ai_specific/c4_walkthrough.md` 的 NVDA 数字是教学示例（口径矛盾），只学方法，别当事实。

## 执行流程（7 步，对应 `knowledge/frameworks/analysis_checklist.md`）

### Step 0 · 一句话 thesis（P2B-C1）
用 ≤30 字说清该票**当下解决什么具体问题（WHAT）**，再说你比市场更敢下注什么（WHY）。写不出 → 停并说明原因。
⚠️ 产业位置 ≠ 投资 thesis（同一卡位价格可天差地别）。

### Step 1 · 产业链定位
`Read knowledge/frameworks/industry_chain_map.yaml`，确定 target 的：
- 角色（Upstream/Midstream/Downstream/Customer/Support）、子环节、是否跨角色；
- 护城河来源 + 5 维 value_capture 分数（王者/二线/代工 → 决定持仓久期）；
- `depends_on` 上游依赖 + `chokepoint`/集中度风险 + 所属 `chokepoint_chains`。
若 target 不在地图中：用其业务归入最接近的角色，并标注「地图外，需自建定位」。

### Step 2 · 拉实时数据（必做，知识库之外）
用 WebSearch / WebFetch 取 `as_of_date` 前后的一手数据：最近季度营收/毛利/营业利润率、capex 及**二阶导**、guidance、RPO/backlog 及客户集中度、估值倍数（fwd P/E、EV/Rev、PEG、Rule of 40）、近 90 天 catalyst 日历（财报日、行业大会）。
先核对**财年**（NVDA Feb-Jan、MSFT Jul-Jun、ORCL Jun-May…）再定 catalyst 时点。术语口径查 `knowledge/frameworks/valuation_toolkit.md`。

### Step 3 · 填 4 维 thesis
按 `knowledge/frameworks/thesis_4dim_template.yaml` 填一份 YAML：
- WHAT = `view`(bull/bear/neutral/watching) + `supports`(3-5 条，**每条带数字+出处**)
- WHY = `core_thesis`(1-2 句差异化判断) + `confidence`(high/medium/low)
- SO WHAT = `catalysts_90d`(带日期+look_for) + `price_outlook`(current + base/bull/bear 锚定当前价)
- RISKS = `red_flags`(2-3 条，**每条带可观察 trigger**)

把填好的 YAML 写到临时文件并机检：
```bash
python3 scripts/validate_thesis.py <thesis.yaml> --as-of <as_of_date>
```
校验**不通过则回到对应维度补全**，直到 5 项全过。硬约束：90 天内无 catalyst → `confidence` 必须 low 或 `view: watching`。

### Step 4 · 估值 + 安全边际（`knowledge/frameworks/valuation_toolkit.md`）
- AI/成长股优先**反向 DCF**：反推当前价隐含增长，判断是否合理；辅以多重估值与历史/同业对比。
- 给**公允价值区间**（非单点）；安全边际 = 区间下方 20-30% 才入场。
- 把关键术语数字（capex 二阶导、RPO 集中度、GAAP/non-GAAP gap、Rule of 40）回填进 supports / red_flags。

### Step 5 · 交叉验证 + 偏差自检（`knowledge/frameworks/mental_models_and_biases.md`）
- 5 心智模型：护城河四维打分、能力圈三问、逆向写 5 个失败场景+触发器。
- 6 偏差自检：view 是确认偏误吗？price_outlook 锚定了买入价吗？是否 FOMO/近因驱动？
- base rate：用 dotcom/mobile 锚 bear 档；2026-28 应用 ROI 滞后窗口，−30%~−50% 回撤纳入 bear 情景。

### Step 6 · 仓位 + 输出判断（P2A-C4）
- 仓位 ≈ 信念 × 赔率 ÷ 风险，由 confidence 映射；约束：单仓 ≤15-20%、留 15-20% 现金、板块 ≤50%、供应链 ≤40%（AI 供应链相关性高，别低估）。
- 论点失效（red_flag trigger 触发）即退出。
- 按下方契约输出。

## 输出渲染（由 `report` 决定）
- **structured**：下方 §输出契约 的 YAML（存档/机读，进 `examples/`）。
- **trader**：交易员速览，套 `assets/trader_report_template.md`（结论→为什么→催化剂→价格剧本→跑路信号，去术语、可直接挂单设止损）。速览由契约字段映射而来，模板内含渲染规则。
  **最终输出 = 一份带日期的独立文件，写到 `reports/<TICKER>_<as_of_date>.md`**（如 `reports/MU_2026-06-15.md`），文件头含日期/信号/现价/仓位，文末附数据时点、来源、底稿 YAML 路径。
- **both**（默认）：先 trader 速览，再附 structured 契约。

无论哪种 report，**完整 thesis YAML 始终生成并经 `validate_thesis.py` 校验后存档**；trader 速览只是它的通俗渲染，不可脱离校验单独产出。

## 输出契约（structured）
```yaml
one_liner_thesis: "≤30 字"
chain_position:
  role: ___          # upstream/midstream/downstream/customer/support
  sub_segment: ___
  moat_source: ___
  value_capture_tier: ___   # 王者/二线/代工
  depends_on: [___]
  concentration_risks: [___]
thesis_4dim: <填好且通过校验的 thesis_4dim_template.yaml>
valuation:
  method: ___        # 反向 DCF / 多重 / DCF
  fair_value_range: "$___ - $___"
  implied_growth: "___%"
  margin_of_safety_entry: "$___"   # 区间下方 20-30%
cross_check:
  moat_score: "_/4"
  circle_of_competence: pass | fail
  inversion_scenarios: [___]       # 5 个失败场景+触发器
  bias_flags: [___]                # 自检发现的偏差
decision:
  call: buy | hold | sell
  target_position_pct: "___%"
  monitors:
    catalysts: [{date, look_for}]
    red_flag_triggers: [___]
data_freshness_note: "数据核实于 <as_of_date>，来源：<...>"
```

最后附 `knowledge/frameworks/analysis_checklist.md` 的 **Review 节奏**（周/月/季）提醒。

## 资产索引
- 产业链定位：`knowledge/frameworks/industry_chain_map.yaml`
- 4 维 schema + 范例：`knowledge/frameworks/thesis_4dim_template.yaml`
- 估值 + 术语：`knowledge/frameworks/valuation_toolkit.md`
- 心智模型 + 偏差 + base rate：`knowledge/frameworks/mental_models_and_biases.md`
- 主流程 SOP：`knowledge/frameworks/analysis_checklist.md`
- 交易员速览模板：`assets/trader_report_template.md`（`report: trader` 用）
- thesis 校验器：`scripts/validate_thesis.py`
- 回归样例（thesis 底稿 YAML）：`examples/`（nvda / mu，2026-06-15）
- 最终交易员研报（带日期独立文件）：`reports/<TICKER>_<as_of_date>.md`
- 深挖（可选）：`knowledge/part1_industry/`、`part2a_general/`、`part2b_ai_specific/` 逐章笔记（按 chapter/tag 检索）——因源自第三方课程**默认未随仓库分发**，主流程不依赖，存在则可用
