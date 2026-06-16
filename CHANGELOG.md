# Changelog

本项目所有重要变更记录于此。
格式参考 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，版本遵循语义化版本。

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
