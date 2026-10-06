---
name: ai-stock-analysis
description: >
  股票研究与投研报告 skill。用于分析/研究单只股票、公司、行业或产业链标的，
  包括美股/海外 AI 产业链股票（如 NVDA、ASML、MU、CoreWeave、光模块、算力链）
  和 A 股公司/代码（如 688082、688981、盛美上海、中芯国际、半导体设备、国产算力）。
  先识别市场并分流：美股/海外（含韩台日 AI 链）走 AI 产业链 thesis + 实时行情 + 长短期判断；
  A 股/港股走最新数据源 + 产业链路径 + 12 章深度研报 + DCF/DDM/杜邦估值 + 长期/短期评价。
  也用于复盘历史 thesis（mode=review：对照实际走势、校准 confidence、重写或作废旧 thesis）。
---

# 股票研究路由 skill

把用户给定的 `target` 先分成 **A 股 / 港股**（沪深港，走同一套深度研报模式）或 **美股/海外市场**（含韩国/台湾/日本 AI 链标的），再加载对应工作流。不要混用数据源；A 股和港股都不套 Hyperliquid 合约逻辑。

## 输入
`{ target: <ticker/代码/公司名/主题>, as_of_date: <YYYY-MM-DD，默认今天>, mode: full | quick | review, report: both | trader | structured | a_share_deep }`

- `mode=full`：默认完整流程；`quick`：事件速评/简版，但仍要标明数据来源和失效条件。
- `mode=review`：复盘历史 thesis（见下方「复盘模式」）。用户说「复盘」「回看之前的分析」「thesis 还成立吗」时用。
- `report`：
  - 美股/海外默认 `both`，可用 `trader` 输出交易员速览。
  - A 股默认 `a_share_deep`，生成 Markdown 到 `reports/`。

## 文件命名规范（各市场统一）

输出文件名格式：`reports/<日期>_<标的>_<市场>.md`（用 `_` 分隔，文件名不含空格）

- `<日期>`：`YYYY-MM-DD`（= `as_of_date`）。
- `<标的>`：A 股/港股用 `中文简称代号`（名称与代号直接相连，不加空格，如 `盛美上海688082`、`腾讯控股00700`）；美股/海外用 `TICKER`（如 `NVDA`）。
- `<市场>`：英文。A 股 = `A-share`；港股 = `HK`；美股 = `US`；韩国 = `KR`；台湾 = `TW`；日本 = `JP`。按**分析所用的交易标的**定市场：SK Hynix 用 KRX 本地股分析 → `KR`；用其美国 ADR 分析 → `US`。韩台日标的的 `<标的>` 用英文简称（如 `SKHYNIX`、`TSMC`、`ADVANTEST`）。
- 示例：`reports/2026-06-26_盛美上海688082_A-share.md`、`reports/2026-06-26_腾讯控股00700_HK.md`、`reports/2026-06-26_NVDA_US.md`。

## Step 0 · 市场识别（必须先做）

按以下顺序判断：

1. **A 股**：代码形态为 `600/601/603/605/688/689/000/001/002/003/300/301/430/8xx/920`，带 `.SH/.SZ/.BJ`，或中文 A 股公司名（如盛美上海、中芯国际、贵州茅台、宁德时代）。
2. **港股**：5 位数字代码（常带前导零，如 `00700` 腾讯、`09988` 阿里、`03690` 美团、`01810` 小米），带 `.HK`，或明确说港股/H 股/港股通标的。**港股与 A 股走同一套深度研报模式**（见下方 A 股/港股路径）。
3. **美股/海外**：英文 ticker（如 `NVDA`、`MU`、`ASML`、`TSM`、`MSFT`）、海外上市公司名、或明确说美股/海外（非港股）。
4. **韩国 / 台湾 / 日本**：`.KS/.KQ`（如 `000660.KS` SK Hynix、`005930.KS` 三星）、`.TW/.TWO`（如 `2330.TW` 台积电）、`.T`（如 `6857.T` Advantest、`8035.T` 东京电子），或用户明确指韩股/台股/日股。走**美股/海外 AI 产业链流程**，差异：
   - 价格：先查 HL 是否有美元 perp（如 `hl_price.py SKHYNIX` → `xyz:SKHX`）；本地股分析须用交易所现货价并标明币种（KRW/TWD/JPY），**不要把 HL 美元价与本地币价混用**；
   - 财报：KRX DART / 台湾公开资讯观测站 / 东证 TDnet 一手披露，季度财报节奏与美股不同，催化剂日期按本地公告；
   - thesis 的 `price_outlook` 全部用同一币种。
5. **不确定**：先问用户确认交易市场；不要猜。

识别后只走对应路径：

- A 股 / 港股：读取 `knowledge/markets/a_share_workflow.md`，并按需读取 `a_share_data_sources.md`、`a_share_industry_chain_map.yaml`、`assets/a_share_report_template.md`。
- 美股/海外/韩台日：读取 `knowledge/frameworks/analysis_checklist.md`，沿用现有 AI 产业链 7 步流程。
- `mode=review`：不分市场，走下方「复盘模式」。

## 共性铁律

1. **最新数据优先**：所有进入结论的价格、财务、估值、股东、客户、订单、capex、技术指标，都必须在本次执行中核实并标明来源和日期。
2. **数字可追溯**：报告里不能用无出处的核心数字；不确定就写“不足以核实”，不要补脑。
3. **先 thesis 后动作**：写不出一句具体 thesis，就不要给买卖建议。
4. **长期和短期分账**：长期配置价值与短期交易窗口必须分开判断，可得出不同结论。
5. **隐私保护**：skill 不内置手机号、账号、访问令牌、外发频道 ID、私聊 ID、代理地址；不得自动发送报告到外部渠道，除非用户在当次会话明确提供并确认。

## A 股 / 港股路径（路由到 `knowledge/markets/a_share_workflow.md`）

适用：A 股、港股个股深度报告、行业/对比报告、财报/事件速评。两市共用 12 章框架与估值三件套；区别只在数据源、代码形态、币种和资金面口径（港股看南向资金 + HKD，详见 `a_share_data_sources.md` 的港股补充）。

核心输出：

- 默认写入 `reports/<日期>_<中文简称代号>_<A-share|HK>.md`（A 股用 `A-share`，港股用 `HK`；见上方命名规范）。
- 深度报告包含 12 章：公司概况、五年经营、客户结构、股东结构、管理团队、行业格局、研发/capex、风险、估值、竞争对手、技术分析、综合结论。
- 估值章节必须包含 WACC 逐步计算、FCF 基准推导、ROE×留存率增长锚、DCF 敏感性矩阵、DDM 三阶段、PE/PB/PEG 相对估值、杜邦三因子。
- 产业链路径必须写清：上游依赖 → 公司卡位 → 下游客户/场景 → 卡点/替代/政策风险 → 同链标的对照，并给价值捕获评分（5 维打分 + 卖铲子/制造平台/应用兑现/周期跟涨 定档）。
- 结论必须分：
  - 长期：配置价值、目标仓位、估值安全边际、季度复盘指标。
  - 短期：趋势/事件交易、买入区、止损、止盈、催化剂、失效条件。

交付前运行：

```bash
python3 scripts/validate_a_share_report.py reports/<日期>_<中文简称代号>_<A-share|HK>.md
```

校验失败必须补全报告，不交付半成品。

## 美股/海外路径（现有 AI 产业链流程）

适用：美股/海外 AI 产业链个股、公司、板块或主题。

执行 `knowledge/frameworks/analysis_checklist.md` 的 7 步：

1. 一句话 thesis（≤30 字，先 WHAT 后 WHY）。
2. 读取 `knowledge/frameworks/industry_chain_map.yaml` 做产业链定位。
3. 拉实时数据。价格主源优先 `python3 scripts/hl_price.py <TICKER> --candles 20`（自动在各 HIP-3 dex 中选最活跃的盘，输出 ATR14 / MA50 / MA200 / 交易时段）；未上 Hyperliquid 时回退现货价，并标注来源。财务序列可用 `python3 scripts/sec_facts.py <TICKER>`（SEC EDGAR，美股）。同时按 checklist Step 2 写「市场状态」：相对强弱、均线位置、板块轮动。当期基准数查 `knowledge/frameworks/market_snapshot_2026Q3.yaml`，并核对其 `as_of` 是否过期。
4. 按 `knowledge/frameworks/thesis_4dim_template.yaml` 填 4 维 thesis（含 `as_of_date`），运行 `scripts/validate_thesis.py`。
5. 用 `knowledge/frameworks/valuation_toolkit.md` 做估值和安全边际。**存储 / 半导体设备 / 材料等周期股必须走「方法 4 · 周期股估值」**（正常化 P/E + 周期位置信号），不得只凭低 fwd P/E 判断低估。
6. 用 `knowledge/frameworks/mental_models_and_biases.md` 做心智模型与偏差自检。
7. 输出长期正股 / 短期 Hyperliquid 合约两个角度的结论。短期仓位按 ATR 计算：止损距离 ≥ 1.5×ATR14，单笔风险 ≤ 账户 1%，杠杆 ≤ maxLev 且由「风险 ÷ 止损距离」推出，而不是先定杠杆倍数。
8. 同一标的已有历史 thesis 时，先跑 `python3 scripts/review_theses.py examples/<旧底稿>.yaml`，在报告开头写一句上次判断的结果（命中 / 落档 / 哪条 trigger 触发）。

美股/海外最终报告写到 `reports/<日期>_<TICKER>_<US|KR|TW|JP>.md`（见上方命名规范），完整 thesis YAML 存档到 `examples/<日期>_<TICKER>_<市场>.yaml`。

## 复盘模式（mode=review）

用途：把历史 thesis 和之后的实际走势对照，校准 confidence，决定重写还是作废。

1. 运行 `python3 scripts/review_theses.py [examples/<底稿>.yaml ...] --write` → `reports/<日期>_thesis复盘_US.md`（默认扫全部 `examples/`）。脚本给出：90 天窗口状态、窗口末价落档（bear/base/bull/档外）、方向命中、短期计划先止损还是先止盈、按 confidence 汇总命中率。
2. 对每份方向 ✗ 或落在档外的 thesis，人工补一段归因：哪条 support 失效、哪个 red_flag trigger 先触发、是否属于周期股估值误判。系统性问题写进 `docs/issues.md`。
3. 校准：同一 confidence 档的方向命中率明显偏低时，下一份 thesis 降一档 confidence；情景经常落在档外，就放宽 bull/bear 区间。
4. 窗口已结束且用户仍关注的标的：按 full 流程重写 thesis（新 `as_of_date`），旧底稿保留不改，作为复盘样本。
5. 非美元计价或未上 HL 的 thesis，脚本会标「需现货复盘」，由 agent 联网取现货收盘价补齐。

## 资产索引

- 美股/海外主流程：`knowledge/frameworks/analysis_checklist.md`
- 美股/海外产业链：`knowledge/frameworks/industry_chain_map.yaml`
- 当期基准数（带日期，唯一出处）：`knowledge/frameworks/market_snapshot_2026Q3.yaml`
- 美股/海外 thesis schema：`knowledge/frameworks/thesis_4dim_template.yaml`
- 通用估值与偏差：`knowledge/frameworks/valuation_toolkit.md`、`knowledge/frameworks/mental_models_and_biases.md`
- A 股主流程：`knowledge/markets/a_share_workflow.md`
- A 股数据源：`knowledge/markets/a_share_data_sources.md`
- A 股产业链路径：`knowledge/markets/a_share_industry_chain_map.yaml`
- A 股报告模板：`assets/a_share_report_template.md`
- 美股交易员模板：`assets/trader_report_template.md`
- 校验器：`scripts/validate_thesis.py`、`scripts/validate_a_share_report.py`
- 取数：`scripts/hl_price.py`（HL 价格 + ATR/均线）、`scripts/sec_facts.py`（SEC 财务序列 / 云厂商 capex 二阶导）
- 复盘：`scripts/review_theses.py`
