# AGENTS.md — stocks-ai-taste-skill

股票研究路由 skill 项目。入口 `SKILL.md` 先识别市场，再分流到美股/海外 AI 产业链流程或 A 股 / 港股研报流程（沪深港共用一套深度模式）；知识库 + 模板 + 校验器配套维护。

## 运行方式（分析个股）
当用户要求「分析 <ticker/公司/主题>」（如「分析 NVDA」「分析 MU report=trader」）时：
1. 读 `SKILL.md`，先做市场识别：A 股 vs 美股/海外；不确定就问用户，不猜。
2. **美股/海外路径**：严格按现有 7 步流程执行（产业链定位 → 拉实时数据 → 4 维 thesis → 估值 → 偏差自检 → 双角度输出）。
3. **美股价格主源 = Hyperliquid 美股 perp**：先跑 `python3 scripts/hl_price.py <TICKER>`（mark/oracle + 日线 + 资金费 + 最大杠杆，无需 key）；退出码 3=未上 HL→回退联网搜索现货价。
4. **A 股 / 港股路径**：读取 `knowledge/markets/a_share_workflow.md`，按最新数据源、产业链路径、12 章深度研报、估值三件套、长期/短期双角度执行。港股共用此流程，仅数据源（港交所披露易/南向资金）、代码形态（5 位 .HK）、币种（HKD）有别；不套 Hyperliquid。
5. 美股最终报告写到 `reports/<日期>_<TICKER>_US.md`，4 维 thesis 底稿写到 `examples/<ticker>_<日期>.yaml`，并跑 `python3 scripts/validate_thesis.py` 机检通过。
6. A 股/港股研报写到 `reports/<日期>_<中文简称代号>_<A-share|HK>.md`，套 `assets/a_share_report_template.md`，并跑 `python3 scripts/validate_a_share_report.py` 机检通过。
   - 命名规范（三市统一）：`reports/<YYYY-MM-DD>_<标的>_<市场>.md`，用 `_` 分隔不含空格；标的——A 股/港股用 `中文简称代号`（如 `盛美上海688082`、`腾讯控股00700`）、美股用 `TICKER`；市场——`A-share` / `HK` / `US`。
7. 非 AI 产业链标的：美股/海外改用通用股票模型并显著免责；A 股仍按 A 股研报框架走，不强行套 AI 产业链。

## 项目结构
- `SKILL.md` — skill 主体（7 步流程 + I/O 契约）
- `knowledge/markets/` — A 股分流流程、数据源、产业链路径
- `scripts/hl_price.py` — 价格主源取数（Hyperliquid 美股 perp，mark/oracle + 日线，无需 key）
- `scripts/validate_thesis.py` — 4 维 thesis 校验器（操作化 P2B-C2 的 5 项自检）
- `scripts/validate_a_share_report.py` — A 股 Markdown 研报校验器
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
- A 股报告必须标明数据源日期；优先用同花顺/巨潮/交易所公告/东方财富/公司财报等最新来源。
- 隐私保护：skill 不内置手机号、账号、访问令牌、外发频道 ID、私聊 ID、代理地址；不自动发送外部渠道。
- 已知转写订正：CEG=Constellation、NBIS=Nebius、CRWV=CoreWeave。
