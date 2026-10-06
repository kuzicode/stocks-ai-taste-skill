# Changelog

本项目所有重要变更记录于此。
格式参考 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，版本遵循语义化版本。

## [0.3.0] - 2026-10-06

### Added
- **复盘模式 `mode=review`** + `scripts/review_theses.py`：按 thesis 的 `as_of_date` 取 90 天窗口的 HL 日线，输出落档（bear/base/bull/档外）、方向命中、短期计划先止损还是先止盈，以及按 confidence 汇总的命中率。
- **周期股估值**（valuation_toolkit 方法 4）：正常化 P/E、P/B 分位、周期位置信号表、硬规则（周期高位禁止只凭低 fwd PE 判低估，bear 档含 −40%~−50%）。
- `knowledge/frameworks/market_snapshot_2026Q3.yaml`：带日期、标可信度的当期基准数（capex 指引与 SEC 实际 TTM、NVDA / MU / SK Hynix / AVGO 最新季度、市场状态、AI 实验室上市状态、HL 股票永续）。
- `scripts/sec_facts.py`：SEC EDGAR 季度财务序列（YTD 相减还原单季），`--capex` 给出云厂商 TTM capex 及其二阶导。
- analysis_checklist Step 2b「市场状态」（均线偏离、相对强弱、拥挤度、轮动），以及按 ATR 计算短期仓位。
- SKILL Step 0 新增韩国 / 台湾 / 日本分支（`KR` / `TW` / `JP`）。

### Changed
- `hl_price.py`：遍历 HIP-3 dex，按流动性选盘，过期盘标 stale；新增 ATR14、MA50 / MA200、mark-oracle 基差、美股交易时段与 price_caveat；SKHYNIX 默认映射到 xyz:SKHX。
- `validate_thesis.py`：as-of 优先读 thesis 的 `as_of_date`；新增规则 6（杠杆 ≤ maxLev）和规则 7（止损在入场区正确一侧）。
- `industry_chain_map.yaml`：补测试设备、NAND / HDD、玻璃 / 光纤、高速互联、光传输、矿企 neocloud、新电力；加 `cyclical` 标记；de-rate 触发器改为相对口径；客户层加入上市状态和上市后的归类规则。
- 旧报告与底稿按命名规范改名（本地运行期文件）；阶段 1-4 计划归档。

### Fixed
- 旧 thesis 重跑时 as-of 漂移导致误报（ISS-002）。
- 港股 / 韩股报告误用 `_US` 后缀（ISS-004）。

## [0.2.0] - 2026-06-16

### Added
- **价格主源接入 Hyperliquid 美股 perp**：新增 `scripts/hl_price.py`，封装公开 info API（dex=`xyz`，符号 `xyz:<TICKER>`），输出 `mark`/`oracle`/`mid`、资金费（时/年化）、最大杠杆、未平仓、近 N 日线高低区间；**无需 API key**。未上 HL 的标的退出码 3 → 调用方回退 WebSearch 现货价。
- **机构目标价交叉锚**：输出契约与 thesis 模板新增 `analyst_targets`（高/中位/低 + 家数 + 来源），与自算公允价区间并列；现价高于机构共识时作为反共识信号。
- **双角度结论**：`decision` 拆为 `long_term`（正股长期持有：call + 仓位 + 安全边际加仓区）与 `short_term`（Hyperliquid 合约杠杆：方向 + 保守杠杆≤maxLev + 入场/止损/止盈 + 资金费成本）。

### Changed
- `SKILL.md`：Step 2 增「价格主源=HL + 机构目标价必拉」，Step 4 增机构目标价交叉锚，Step 6 重构为双角度判断；输出契约新增 `analyst_targets`/`hl_market`/双角度 `decision`。
- `assets/trader_report_template.md`：速览拆「🎯 长期(正股) / ⚡ 短期(HL 杠杆)」两块 + 机构目标价行，更新渲染规则与 MU 范例。
- `knowledge/frameworks/thesis_4dim_template.yaml`：`price_outlook` 下新增 `analyst_targets`（附加字段，不破坏 5 项校验）。
- `AGENTS.md` / `README.md` / `docs/skill_design.md`：同步价格主源优先级与双角度输出契约。

### Fixed
- 文件夹更名 `stocks-taste-skill` → `stocks-ai-taste-skill`，修正 `AGENTS.md` / `docs/plan.md` 标题中的残留旧名。

### Verified
- `hl_price.py` 实测：NVDA(20x) / CRWV(10x) / MU(10x) 正常返回，未上 HL 标的退出码 3。
- 端到端实跑 MU（2026-06-16）：HL mark $1060 + 44 家机构目标价 + 双角度结论，底稿过 `validate_thesis.py` 5 项机检。

## [0.1.0] - 2026-06-15

### Added
- 首版 AI 产业链股票分析 skill：`SKILL.md`（7 步流程 + I/O 契约）。
- 原创综合资产 `knowledge/frameworks/`：产业链地图、4 维 thesis 模板、估值工具箱、心智模型与偏差、分析 SOP。
- `scripts/validate_thesis.py`：4 维 thesis 校验器（操作化 P2B-C2 的 5 项自检）。
- `assets/trader_report_template.md` 交易员速览模板；`docs/skill_design.md` 设计蓝图。
- 多 agent harness 入口 `AGENTS.md` + `CLAUDE.md` pointer；`README.md` 与安装/使用说明。
