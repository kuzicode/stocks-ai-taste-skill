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
- 当期基准数先读 `market_snapshot_2026Q3.yaml`；分析日距其 `as_of` 超过 100 天 → 在报告里注明快照过期，关键数重新核实。
- 美股财务序列：`python3 scripts/sec_facts.py <TICKER>`（最近 8 个季度营收/毛利率/营业利润/capex/FCF，SEC EDGAR 一手）。

### Step 2b · 市场状态（2026-10 新增：7 月半导体回撤事前没有任何信号）
基本面 thesis 解释不了拥挤与轮动，短期结论前必须写这 4 行（数据来自 `hl_price.py` 输出 + 联网）：
1. **趋势位置**：现价相对 MA50 / MA200 的偏离（`hl_price.py` 直接给）。偏离 MA200 >+40% 视为拉伸，短期只做回踩不追高。
2. **相对强弱**：近 20 / 60 日涨跌幅 vs `SMH`（半导体）或 `XYZ100`（大盘），可用 `hl_price.py SMH` 取对照。
3. **拥挤度**：HL 资金费年化 >30% 或 OI 快速上升 = 多头拥挤；RSI / 卖方报道里的「极端超买」只作佐证。
4. **轮动**：本季资金在「卖铲子（芯片/存储/设备）」与「买铲子（云厂商/应用）」之间往哪边流（看 snapshot 的 regime 段 + 最近一次财报季的股价反应）。
→ 4 行里 ≥2 行偏负面时，短期结论不得给「追多」，最多给「回踩做多」并写明回踩价位。

## Step 3 · 填 4 维 thesis（thesis_4dim_template.yaml）
按模板填 WHAT(view+supports) / WHY(core_thesis+confidence) / SO WHAT(catalysts_90d+price_outlook) / RISKS(red_flags+trigger)。
**完成自检 5 项全 yes**：① view 单点明确 ② 每条 support 带数字+出处 ③ 每条 red_flag 带可观察 trigger ④ 90 天内 ≥1 catalyst（否则 confidence=low/view=watching）⑤ price_outlook 锚定当前价。

## Step 4 · 估值 + 安全边际（valuation_toolkit.md）
- AI/成长股优先**反向 DCF**：反推当前价隐含的增长，判断是否合理。
- **周期股（chain_map 里 `cyclical: true`：存储 / 设备 / 测试等）必须走「方法 4 · 周期股估值」**：给正常化 P/E 与周期位置信号，bear 档含 −40%~−50% 情景，confidence 最高 medium。
- 多重估值与历史/同业对比；给**公允价值区间**（非单点）。
- 安全边际：区间下方 **20-30%** 才入场。
- 把术语数字（capex 二阶导、RPO 集中度、GAAP/non-GAAP gap、Rule of 40 等）回填进 supports / red_flags。

## Step 5 · 交叉验证 + 偏差自检（mental_models_and_biases.md）
- **5 心智模型**：护城河四维打分、能力圈三问、逆向写 5 个失败场景+触发器。
- **6 偏差自检**：我的 view 是确认偏误吗？price_outlook 锚定了买入价吗？是否在 FOMO/近因驱动？
- **base rate 校准**：用 dotcom/mobile 锚定 bear 档；2026-28 应用 ROI 滞后窗口，−30%~−50% 回撤入 bear 情景。

## Step 6 · 仓位 + 输出判断（P2A-C4）
- 仓位 ≈ 信念 × 赔率 ÷ 风险；由 confidence 映射：单仓上限 15-20%、留 15-20% 现金、板块 ≤50%、供应链 ≤40%（注意 AI 供应链相关性高，别低估）。
- **短期合约按 ATR 定仓**（`hl_price.py` 输出 ATR14）：
  1. 止损距离 = max(结构位到入场价的距离, 1.5 × ATR14)；
  2. 名义仓位 = 账户 × 单笔风险%（默认 1%）÷ 止损距离%；
  3. 杠杆 = 名义仓位 ÷ 分配保证金，必须 ≤ maxLev，并且「止损距离% × 杠杆」远小于 100%（离强平价留足空间）；
  4. 持有期资金费成本 = 年化资金费 × 持有天数 / 365 × 杠杆，写进 funding_cost_note。
  先有止损和风险，再推出杠杆；不要先拍一个倍数。
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
- **季（90 天）**：thesis 被证实/证伪，校准 confidence；4 季累积 = 个人 thesis 库。用 `python3 scripts/review_theses.py --write` 出命中表（SKILL `mode=review`）。

## 时效性缺口（务必声明）
本库知识截至原文（2025-26），不含实时行情/财报。Step 2 的实时数据是判断质量的前提；任何引用本库的具体数字都须回查一手来源。
