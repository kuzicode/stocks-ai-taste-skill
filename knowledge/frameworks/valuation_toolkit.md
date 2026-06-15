# 估值工具箱（valuation_toolkit）

> 主数据源：P2A-C1（估值基础）+ P2B-C3（AI 财报术语词典）。
> 数据口径警告：下列基准数（毛利率/倍数/capex）均为原文快照，使用前回查最新财报。

## 0. 核心心法
**Price is what you pay, value is what you get.** 公允价值是一个**区间（band）**，不是单点。
散户三宗罪：① 只看单一 P/E ② 没有公允价值区间 ③ 没有安全边际纪律。结论必须落到「**区间 + 安全边际 + 风险**」三件套。

---

## 1. 三种估值方法

### 方法 1 · DCF（折现现金流）— 适合成熟稳定现金流
```
Value = Σ ( 年度 FCF / (1 + WACC)^year ) + Terminal Value
Terminal Value = 末年 FCF × (1 + g) / (WACC − g)
```
- WACC 折现率常取 8-12%（例用 10%）；永续 g 取 2-3%。
- **陷阱**：终值常占总价值 70%+（例中 76%），结果对 WACC/g 微小变化极度敏感 → 必做敏感性分析，给区间不给单点。
- **对 AI/高增长股不可靠**：10 年 FCF 预测受 capex 轨迹、客户集中度、毛利可持续性、scaling law 不确定性侵蚀。

### 方法 2 · 多重估值（Multiples）— 适合横向/历史对比
- 取 fwd P/E、PEG、EV/Revenue、EV/EBITDA、P/B；
- 与公司**自身 5 年历史区间**比（历史百分位）+ 与**同业 peer**比（相对贵贱）。
- 不擅长给绝对公允价值。

### 方法 3 · 反向 DCF（Reverse DCF）— 适合 AI/成长股（推荐）
- 把当前股价当已知，**反推它隐含的增长假设**，再判断该增长是否合理/能兑现。
- 范例（NVDA $135，fwd P/E 30x，假设成熟期终值 P/E 15x）→ 反推隐含 5 年 EPS 年增约 26% → 判断 26% 合不合理，比硬预测 10 年 FCF 更可靠。

### 方法适用性速查
| 方法 | 擅长 | 不擅长 |
|---|---|---|
| DCF | 成熟稳定（Coca-Cola/J&J） | 高增长 AI |
| 多重 | 多数公司、同业对比 | 绝对公允价值 |
| 反向 DCF | AI/成长股、检验假设 | 成熟稳定公司 |

### 安全边际（Margin of Safety, Graham 1934）
- 公允价值区间**下方 20-30%** 才入场，作为分析误差/下跌/黑天鹅的缓冲。
- 公允价值 $100 → 在 $70-80 进，而非 $99。

---

## 2. 财报术语词典（按 4 维分组）

> 用法：每个术语先归入 WHAT/WHY/SO WHAT/RISKS 某一维，再看数字；被跳过的术语会在论点里留缺口。

### WHAT 维（当前叙事 / 支撑）
| 术语 | 定义 / 计算 | AI 用法与陷阱 |
|---|---|---|
| Segment Revenue 分部营收 | 各分部 / 总营收 | 看是否单腿依赖。NVDA 数据中心约 88% |
| **Backlog / RPO** 剩余履约义务 | 已签未确认收入 | 未来收入可见度；**须拆集中在谁**（ORCL RPO 约 54% 来自 OpenAI = WHAT 支撑 + RISKS 红旗，跨维） |
| **Capex 二阶导** | capex 指引增速的增速 | **看方向不看绝对值**；二阶导=0 → 全链 de-rate；警戒 FY27 指引 YoY<10% |
| Wafer/HBM 产能 | 物理出货上限 | 需求爆棚也受产能封顶（TSM 3nm、SK Hynix HBM） |
| Hyperscaler vs Neocloud | 通用云 vs AI 专用云 | Neocloud 增速猛但客户极集中（CRWV 约 60% 靠 MSFT） |

### WHY 维（核心论点 / 信心）
| 术语 | 定义 | 陷阱 |
|---|---|---|
| Pre-announcement / Guidance | 财报前约 2 周透露 / 前瞻指引 | 指引常比当期实际更驱动股价 |
| Smart Money Divergence | 机构持仓矛盾 | 单一 13F 不可靠；要解释分歧而非盲从 |

### SO WHAT 维（价格 / 催化剂）
| 术语 | 定义 / 计算 | 基准 / 阈值 |
|---|---|---|
| Revenue 营收 | 总销售额 | 健康 AI YoY>50%；<30% 减速警告 |
| Gross Margin 毛利率 | (Rev−直接成本)/Rev | NVDA ~75%、TSM ~53-58%、MU ~35-45%；上行=定价权 |
| Operating Margin 营业利润率 | (Rev−全部经营成本)/Rev | MSFT ~45%、NVDA 60%+、TSM ~47%、AMD ~7-12% |
| EPS 每股收益 | Net Income/股本 | 区分 GAAP vs non-GAAP |
| FCF 自由现金流 | 经营现金流 − Capex | AI 重资本期可为负（ORCL TTM 约 −$24.7B） |
| Capex 资本开支 | 长期资产购置 | 注意"计划口径"vs"10-K PP&E 实际口径" |
| fwd P/E | 股价/下年 EPS | NVDA 30-35x、MSFT ~30x、MU 8-10x |
| PEG | P/E ÷ EPS 增速% | <1 便宜、>2 偏贵（AI 早期 PEG>2 未必贵） |
| EV/Revenue | 企业价值/营收 | 不盈利/低毛利适用（CRWV 12-15x、SNOW ~13x） |
| EV/EBITDA | 跨资本结构比较 | — |
| Rule of 40 | 增速% + 营业利润率% ≥40% | CRWD ~60% ✓、MDB ~29% ✗ |
| Fiscal Year 财年 | 多数非自然年 | NVDA(Feb-Jan)、MSFT(Jul-Jun)、ORCL(Jun-May)——核催化剂前先核财年 |

### RISKS 维（红旗 / 退出触发）
| 术语 | 红旗条件 |
|---|---|
| GAAP vs non-GAAP Gap | 差距 >20% = 黄旗（SBC 粉饰）；NVDA ~10% 正常，SaaS 常 >40% |
| FCF 转负 | capex/revenue >35% 持续 2 季 + 营收增速 <30% |
| Capex/Revenue 比率 | 健康 15-20%；警戒 30%+；ORCL 逼近 40% |
| **客户集中度** | 单一客户 >50% = 红旗（CRWV 约 60% MSFT；ORCL OCI 约 54%） |
| 13F 局限 | 滞后约 6 周；不含空头/期权（隐藏大额看跌） |
| SBC 股权激励 | GAAP/non-GAAP 差距主因，稀释股东 |
| Token Economics | 单 token 成本，判断 AI 单位经济是否可持续（原文未给公式，需另补） |

---

## 3. 落库提醒
- 「capex 二阶导=0 → 全链 de-rate」是最有操作价值的判断框架 → 做成季度跟踪项（云厂商 capex 指引增速序列）。
- PEG / Rule of 40 / EV/Revenue 阈值为经验值，跨行业/不同利率环境慎用。
- 所有具体数值仅为示例，引用前回查一手 10-K/10-Q/电话会。
