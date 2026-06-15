# AI 个股分析 SOP（analysis_checklist）

> 把全知识库串成一条可执行流水线。主数据源：P2B-C1（先问 WHAT）、P2B-C4（NVDA 6 步 walkthrough）、P2B-C5（ship 清单 + review 节奏）、P2A-C4（仓位管理）。
> 这是未来 skill 的主流程脚手架。

## 输入
一个 ticker / 公司 / 主题。

## Step 0 · 先问「它解决什么问题」（P2B-C1）
- 用一句话（≤30 字）说清这只票**当下解决什么具体问题**（WHAT），再说为何你比市场更敢下注（WHY）。**先 WHAT 后 WHY。**
- 写不出这句 → 不该建仓，停。
- ⚠️ 产业位置 ≠ 投资 thesis（同一卡位 NVDA 可 $14 也可 $230）。

## Step 1 · 在产业链中定位（industry_chain_map.yaml）
- 查该票属哪个角色（Upstream/Midstream/Downstream/Customer/Support）、子环节、是否跨角色。
- 读它的**护城河来源**与**5 维价值捕获分数**（判断王者/二线/代工，决定持仓久期）。
- 画它的**上下游依赖与卡点链**：要盯哪些上游（如 NVDA→ASML/TSM/SK Hynix/COHR）、哪些集中度风险（如 CRWV 60% MSFT）。

## Step 2 · 拉取近况（外部实时数据，知识库之外）
- 文章数据停在 2025-26，**必须用 WebSearch/最新财报补当下数据**：最近季度营收/毛利/capex、guidance、RPO、客户集中度、估值倍数、近期 catalyst 日历。
- 核对财年（NVDA Feb-Jan 等）以定 catalyst 时点。

## Step 3 · 填 4 维 thesis（thesis_4dim_template.yaml）
按模板填 WHAT(view+supports) / WHY(core_thesis+confidence) / SO WHAT(catalysts_90d+price_outlook) / RISKS(red_flags+trigger)。
**完成自检 5 项全 yes**：① view 单点明确 ② 每条 support 带数字+出处 ③ 每条 red_flag 带可观察 trigger ④ 90 天内 ≥1 catalyst（否则 confidence=low/view=watching）⑤ price_outlook 锚定当前价。

## Step 4 · 估值 + 安全边际（valuation_toolkit.md）
- AI/成长股优先**反向 DCF**：反推当前价隐含的增长，判断是否合理。
- 多重估值与历史/同业对比；给**公允价值区间**（非单点）。
- 安全边际：区间下方 **20-30%** 才入场。
- 把术语数字（capex 二阶导、RPO 集中度、GAAP/non-GAAP gap、Rule of 40 等）回填进 supports / red_flags。

## Step 5 · 交叉验证 + 偏差自检（mental_models_and_biases.md）
- **5 心智模型**：护城河四维打分、能力圈三问、逆向写 5 个失败场景+触发器。
- **6 偏差自检**：我的 view 是确认偏误吗？price_outlook 锚定了买入价吗？是否在 FOMO/近因驱动？
- **base rate 校准**：用 dotcom/mobile 锚定 bear 档；2026-28 应用 ROI 滞后窗口，−30%~−50% 回撤入 bear 情景。

## Step 6 · 仓位 + 输出判断（P2A-C4）
- 仓位 ≈ 信念 × 赔率 ÷ 风险；由 confidence 映射：单仓上限 15-20%、留 15-20% 现金、板块 ≤50%、供应链 ≤40%（注意 AI 供应链相关性高，别低估）。
- 分批建仓、季度再平衡、**论点失效（red_flag trigger 触发）即退出**。
- **输出**：买 / 持 / 卖判断 + 目标仓位 + 一份填好的 4 维 thesis YAML + 公允价值区间 + 关键监控项（catalyst 日期 + red_flag trigger）。

---

## Ship 质量门（P2B-C5，合格 thesis 标准）
- [ ] 每条 support 带数字 + 出处
- [ ] 每条 red_flag 带可观察 trigger
- [ ] 显式写了 anti-thesis（反方论点）
- [ ] view 单点、confidence 与 catalyst 一致
- [ ] price_outlook 三档锚定当前价
- [ ] 一句话 thesis ≤30 字、具体、有差异度

## Review 节奏（P2B-C5）
- **周**：catalyst 是否临近、red_flag trigger 是否被触及。
- **月**：「如果现在没仓位，今天还会按此价买吗？」否 → 退出。
- **季（90 天）**：thesis 被证实/证伪，校准 confidence；4 季累积 = 个人 thesis 库。

## 时效性缺口（务必声明）
本库知识截至原文（2025-26），不含实时行情/财报。Step 2 的实时数据是判断质量的前提；任何引用本库的具体数字都须回查一手来源。
