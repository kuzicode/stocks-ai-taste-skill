# 技能设计蓝图 — AI 产业链股票分析 skill

> 状态：**已按本蓝图实现** → `SKILL.md`（主体）+ `scripts/validate_thesis.py`（4 维校验器）。
> 本文档作为设计依据保留；运行入口见根目录 `SKILL.md`。知识底座见 `knowledge/`。

## 1. 目标与触发
- **目标**：给定一只票/公司/主题，输出一份结构化的投资判断（买/持/卖 + 目标仓位 + 4 维 thesis + 公允价值区间 + 监控项）。
- **触发**：用户给定 ticker / 公司名 / 主题（如「分析 NVDA」「看看光模块板块」）。

## 2. 主流程（直接复用 knowledge/frameworks/analysis_checklist.md 的 7 步）
```
输入 ticker
 → Step0 先问「解决什么问题」（≤30 字一句话 thesis；写不出则停）   [P2B-C1]
 → Step1 在 industry_chain_map.yaml 定位角色/护城河/卡点/上下游依赖  [C5/C6/C7]
 → Step2 拉实时数据（WebSearch + 最新财报：营收/毛利/capex/RPO/估值/catalyst 日历）
 → Step3 填 thesis_4dim_template.yaml（WHAT/WHY/SO WHAT/RISKS），过 5 项自检  [P2B-C2]
 → Step4 估值（反向 DCF 优先）+ 安全边际，给公允价值区间          [valuation_toolkit]
 → Step5 5 心智模型交叉验证 + 6 偏差自检 + base rate 校准 bear 档   [mental_models_and_biases]
 → Step6 仓位（信念×赔率÷风险，含上限）+ 输出买/持/卖判断          [P2A-C4]
```

## 3. 输入 / 输出契约
**输入**
```
{ target: "NVDA", as_of_date: "2026-06-15", mode: "full" | "quick" }
```
**输出**
```
{
  one_liner_thesis: "≤30 字",
  chain_position: { role, sub_segment, moat_source, value_capture_tier, depends_on[], concentration_risks[] },
  thesis_4dim: <填好的 thesis_4dim_template.yaml>,
  valuation: { method, fair_value_range, implied_growth, margin_of_safety_entry,
               analyst_targets: { high, median, low, coverage, source } },
  hl_market: { mark, oracle, funding_annual_pct, max_leverage },
  cross_check: { moat_score, circle_of_competence: pass|fail, inversion_scenarios[], bias_flags[] },
  decision: {
    long_term:  { call: buy|hold|sell, target_position_pct, add_zone, rationale },
    short_term: { direction: long|short|观望, leverage, entry, stop_loss, take_profit, funding_cost_note, rationale },
    monitors: { catalysts[], red_flag_triggers[] }
  },
  data_freshness_note
}
```

## 4. 知识库引用方式
- **结构化资产（机读）**：`industry_chain_map.yaml`（定位）、`thesis_4dim_template.yaml`（schema + 校验）→ skill 直接 load。
- **方法资产（指导 prompt）**：`valuation_toolkit.md`、`mental_models_and_biases.md`、`analysis_checklist.md` → 作为流程与评估标准注入。
- **逐章笔记**：作为深挖时的 RAG 检索源（按 tag / chapter 检索）。

## 5. 需要的外部数据源（知识库之外）
- **实时行情主源 = Hyperliquid 美股 perp**（`scripts/hl_price.py`，dex=`xyz`，符号 `xyz:<TICKER>`）：`markPx`/`oraclePx` + 日线 `candleSnapshot` + `funding`（短期杠杆成本）+ `maxLeverage`，公开无需 key；未上 HL 才回退 WebSearch 现货价。
- **机构/分析师目标价**（高/中/低 + 家数 + 来源）：与自算公允价并列做交叉锚。
- 估值倍数（fwd P/E、EV/Rev 等）。
- 最新财报：10-K/10-Q、电话会、guidance、segment revenue、RPO/backlog、capex 及二阶导、客户集中度。
- catalyst 日历（财报日、行业大会如 GTC）；财年口径核对。
- 13F（注意滞后 6 周、不含空头/期权）。
- 候选工具：`scripts/hl_price.py`（价格主源）/ WebSearch / WebFetch / 财经数据 API。

## 6. SKILL.md 骨架草图（仅蓝图，未实现）
```
---
name: ai-stock-analysis
description: 给定 AI 产业链个股，定位产业链位置并按 4 维 thesis 输出投资判断
---
1. 读 knowledge/frameworks/analysis_checklist.md 作为主流程
2. load industry_chain_map.yaml 定位
3. WebSearch 拉实时数据
4. 按 thesis_4dim_template.yaml 填写并自检
5. valuation_toolkit 估值 + mental_models_and_biases 自检
6. 输出 §3 契约的结构化判断
```
配套校验器（建议）：thesis YAML 自动校验「90 天内无 catalyst → confidence 必须 low/watching」「support 必须含数字」「red_flag 必须含 trigger」。

## 7. 时效性缺口（核心风险）
- 知识库截至 2025-26，**所有具体数字须实时复核**；skill 必须在 Step2 强制拉一手数据，并在输出标注 `data_freshness_note`。
- P2B-C4 的 NVDA 数字为教学示例（口径矛盾），仅作方法范例，不可当事实。

## 8. 下一阶段（若推进）
按本蓝图实现 SKILL.md + YAML 校验器 + 实时数据取数层；先用 NVDA/ASML/CRWV 三类（王者/上游/高风险 neocloud）做端到端回归。
