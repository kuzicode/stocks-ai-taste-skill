# 知识框架库 — AI 产业链股票分析

本库是「AI 产业链股票分析并判断投资逻辑」skill 的知识底座，源自 wizzai101.com Part 1（产业）+ Part 2（投资）共 20 篇文章的精读整理（read_date: 2026-06-15）。

> 📦 **分发说明**：`frameworks/` 为原创综合资产，随仓库公开。
> 下方「逐章笔记」（`part1_industry/`、`part2a_general/`、`part2b_ai_specific/`）源自第三方付费课程，
> **默认经 `.gitignore` 屏蔽、不随仓库分发**（本地保留即可，skill 主流程不依赖）。
> 故克隆下来的公开仓库中可能看不到这些逐章文件——这是预期行为。

## 结构

```
knowledge/
├── part1_industry/      产业知识框架（定位个股在产业链中的位置与发展）
├── part2a_general/      通用投资模型（估值/心智模型/历史可比/组合/行为金融）
├── part2b_ai_specific/  AI 特有分析（重点：4 维 thesis 方法论）
└── frameworks/          ★ 跨章综合 / skill 直接调用的资产
```

## 逐章笔记索引

### Part 1 · 产业（定位 + 发展）
| 章 | 文件 | 主旨 |
|---|---|---|
| P1-C1 | part1_industry/c1_history.md | AI 四次寒冬周期；本轮是否「这次不一样」用 5 项可证伪 checklist 验证 |
| P1-C2 | part1_industry/c2_transformer_scaling.md | Transformer + Scaling Laws 让能力「可预测、可买」，是本轮资本开支的技术根因 |
| P1-C3 | part1_industry/c3_why_nvda.md | 战略错误 > 技术错误；CUDA 20 年生态护城河 vs Intel 守 x86 |
| P1-C4 | part1_industry/c4_neural_intuition.md | 用类比讲清 LLM；把 capex 拆成训练 vs 推理两条算力曲线 |
| P1-C5 | part1_industry/c5_hardware_stack.md | 从架构反推硬件瓶颈链 GPU→HBM→互联→液冷→电力，每环=可监控先行信号 |
| P1-C6 | part1_industry/c6_supply_chain.md | ★ 5 角色 + ~52 ticker 因果链；上游护城河最深、下游最浅 |
| P1-C7 | part1_industry/c7_value_capture.md | ★ 5 维评分定王者/代工；营业利润率可差 6 倍 |
| P1-C8 | part1_industry/c8_applications.md | 四应用层 ROI 能否兑现 ~$725B capex = 第 5 次寒冬最大触发点 |
| P1-C9 | part1_industry/c9_geopolitics.md | 美中/出口管制/能源三条地缘 wildcard，须内置进每个 thesis |
| P1-C10 | part1_industry/c10_real_cases.md | 5 真实案例建立直觉：理解产业是为意外发生时判断哪个 thesis 还成立 |

### Part 2A · 通用投资模型
| 章 | 文件 | 主旨 |
|---|---|---|
| P2A-C1 | part2a_general/c1_valuation_basics.md | DCF/多重/反向 DCF 三法 + 安全边际；公允价值是区间 |
| P2A-C2 | part2a_general/c2_mental_models.md | 5 心智模型格栅；逆向问「它怎么死」 |
| P2A-C3 | part2a_general/c3_historical_analogs.md | dotcom/mobile/工业革命做 base rate 风险定价 |
| P2A-C4 | part2a_general/c4_portfolio_construction.md | 仓位=信念×赔率÷风险；单仓/板块/供应链上限 |
| P2A-C5 | part2a_general/c5_behavioral_finance.md | 6 偏差 + 流程对治；最大对手是自己 |

### Part 2B · AI 特有分析（重点）
| 章 | 文件 | 主旨 |
|---|---|---|
| P2B-C1 | part2b_ai_specific/c1_what_problem.md | 先问「解决什么问题」WHAT 优先于 WHY |
| P2B-C2 | part2b_ai_specific/c2_thesis_4dim.md | ★ 4 维 thesis 框架（核心方法论），缺哪维就在哪破 |
| P2B-C3 | part2b_ai_specific/c3_glossary.md | 财报术语按 4 维分组；AI 特有口径（RPO/capex 二阶导/token 经济） |
| P2B-C4 | part2b_ai_specific/c4_walkthrough.md | NVDA 6 步实战演练 |
| P2B-C5 | part2b_ai_specific/c5_write_yours.md | 自己写可证伪、可季度复盘的 thesis |

## 综合框架（skill 直接调用）
| 文件 | 用途 | 来源 |
|---|---|---|
| frameworks/industry_chain_map.yaml | 结构化产业链地图：5 角色×子环节×ticker×护城河×卡点 | C5/C6/C7 |
| frameworks/thesis_4dim_template.yaml | 4 维 thesis 标准 schema（填空模板 + NVDA 范例 + 自检规则） | P2B-C2/C5 |
| frameworks/valuation_toolkit.md | 三种估值法 + 安全边际 + 财报术语词典 | P2A-C1 / P2B-C3 |
| frameworks/mental_models_and_biases.md | 5 心智模型 + 6 偏差 + 历史 base rate | P2A-C2/C3/C5 |
| frameworks/analysis_checklist.md | ★ 端到端 SOP（定位→4 维→估值→自检→判断） | P2B-C1/C4/C5 + P2A-C4 |

## 使用约定（重要）
- **时效性**：全库知识截至原文（2025-26），不含实时行情/财报。任何具体财务数字均为原文快照/估算，**引用前必须回查最新 10-K/10-Q/电话会一手来源**。
- **已知转写订正**：CEG=Constellation Energy（非 Centrus）、NBIS=Nebius（非 Nubis）、CRWV=CoreWeave（非 Crowdstrike）。各笔记「我的批注 / 存疑」段落记录了更多需复核项。
- **方法 vs 事实**：P2B-C4 的 NVDA 数字疑为教学用虚构（guidance 口径自相矛盾），仅作方法范例，不可当事实源。
