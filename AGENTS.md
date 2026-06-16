# AGENTS.md — stocks-ai-taste-skill

AI 产业链股票分析 skill 项目。skill 已实现，入口 `SKILL.md`；知识库 + 校验器配套就绪。

## 运行方式（分析个股）
当用户要求「分析 <ticker/公司/主题>」（如「分析 NVDA」「分析 MU report=trader」）时：
1. 读 `SKILL.md`，严格按其 7 步流程执行（定位 → 拉实时数据 → 4 维 thesis → 估值 → 偏差自检 → 双角度输出）。
2. **价格主源 = Hyperliquid 美股 perp**：先跑 `python3 scripts/hl_price.py <TICKER>`（mark/oracle + 日线 + 资金费 + 最大杠杆，无需 key）；退出码 3=未上 HL→回退联网搜索现货价。其余实时数据（财报/机构目标价/catalyst）用联网搜索现拉（知识库仅 2025-26 快照）。
3. 4 维 thesis 底稿写到 `examples/<ticker>_<日期>.yaml`，并跑 `python3 scripts/validate_thesis.py` 机检通过。
4. 交易员研报写到 `reports/<TICKER>_<日期>.md`（套 `assets/trader_report_template.md`），结论分**长期正股 / 短期 HL 杠杆**两角度，并附机构目标价。
5. 非 AI 产业链标的：改用通用模型并显著免责，不强行套 AI 框架。

## 项目结构
- `SKILL.md` — skill 主体（7 步流程 + I/O 契约）
- `scripts/hl_price.py` — 价格主源取数（Hyperliquid 美股 perp，mark/oracle + 日线，无需 key）
- `scripts/validate_thesis.py` — 4 维 thesis 校验器（操作化 P2B-C2 的 5 项自检）
- `knowledge/frameworks/` — 5 份原创综合资产（skill 直接调用）；逐章精读笔记默认不随仓库分发，见 `knowledge/README.md`
- `docs/plan.md` — 唯一设计权威（Research → Plan → Build）
- `docs/skill_design.md` — skill 设计依据

## 工作流
1. **Research**：读 `docs/plan.md` + `knowledge/`
2. **Plan**：需求变更原地更新 `docs/plan.md`
3. **Build**：按 plan 执行，每步打勾

## 关键约定
- 知识库知识截至原文（2025-26），**任何具体财务数字引用前回查一手 10-K/10-Q/电话会**。
- 核心方法论 = 4 维 thesis（WHAT/WHY/SO WHAT/RISKS），schema 见 `knowledge/frameworks/thesis_4dim_template.yaml`。
- 产业链定位 = `knowledge/frameworks/industry_chain_map.yaml`。
- 已知转写订正：CEG=Constellation、NBIS=Nebius、CRWV=CoreWeave。
