---
last_updated: 2026-10-06
status: active
owner: kumata
---

# 问题记录与经验教训

每次解决非平凡 bug、数据源踩坑、报告质量问题或设计反复后追加一条。

编号使用 `ISS-XXX`，状态为 `open` / `resolved` / `superseded`。

---

<!--
模板：

## ISS-001 — <一句话标题> [open|resolved|superseded]

- 日期：YYYY-MM-DD
- 现象：
- 根因：
- 方案：
- 经验：
-->

## ISS-001 — 存储股把「峰值利润率 + 低 fwd PE」读成低估 [resolved]

- 日期：2026-10-06
- 现象：6 月 3 份存储链 bull thesis（SKHYNIX 06-22 / 06-26、SNDK 06-26 v1）90 天后全部跌破 bear 档（−21%~−27%，`reports/2026-10-06_thesis复盘_US.md`）。SK Hynix Q2（7/29）营业利润率 76% 创新高，但低于预期约 5.5%，股价下跌。
- 根因：valuation_toolkit 只有 DCF / 倍数 / 反向 DCF，没有周期股方法；chain_map 把 MU/SK Hynix 的峰值利润率当护城河证据；bear 档只按 −15%~−20% 设，没有周期回撤情景。
- 方案：valuation_toolkit 加「方法 4 · 周期股估值」（正常化 P/E、P/B 分位、周期位置信号表、硬规则）；chain_map 加 `cyclical: true`；checklist / SKILL Step 5 强制周期股走方法 4。
- 经验：周期高位的低 PE 是风险信号。「beat 但不涨」是顶部预警，MU 9/30 财报（毛利率 86.8%）后股价和 6 月持平，同样符合这一信号。

## ISS-002 — validate_thesis 的 as-of 默认取今天，旧 thesis 重跑后误报 [resolved]

- 日期：2026-10-06
- 现象：2026-10-06 重跑 6 月的底稿，NVDA / MRVL / SNDK / SK Hynix 报「90 天内无 catalyst」。
- 根因：thesis 没有机读的分析日期字段，只写在注释里；`--as-of` 默认取今天。
- 方案：模板加必填 `as_of_date`；校验器优先级改为 `--as-of` > 字段 > 文件头注释（告警）> 今天（告警）；旧底稿已补字段。

## ISS-003 — confidence 没有区分度 [open]

- 日期：2026-10-06
- 现象：12 份美股/海外 thesis 里 11 份 confidence=medium（另一份 000660.KS 也是 medium）；能判断方向的 4 份里只命中 1 份。
- 根因：缺少校准反馈，medium 成了默认选项。
- 方案：`mode=review` + `review_theses.py` 按 confidence 汇总命中率，季度校准。下一步可考虑在校验器里要求 confidence=medium 写出理由（尚未实现）。

## ISS-004 — 韩股 / 港股被命名成 `_US` [resolved]

- 日期：2026-10-06
- 现象：腾讯、泡泡玛特旧报告是 `_US`；SK Hynix（KRX）只能硬塞进 `_US`。
- 根因：Step 0 只有 A 股 / 港股 / 美股三条分支。
- 方案：SKILL Step 0 加韩台日分支（`KR` / `TW` / `JP`，币种不混用）；旧报告与底稿已按规范改名（同日同标的加 `_v1`）。

## ISS-005 — Hyperliquid 冷门 dex 的价格过期 [resolved]

- 日期：2026-10-06
- 现象：2026-10-06 NVDA 在 flx / km / cash / mkts 上也有盘，但 OI=0，mark 为 $197–211；xyz 实际为 $242。
- 根因：HIP-3 允许多个部署方上同一 ticker；旧脚本只认 xyz，迁移到其它 dex 会拿到过期价格。
- 方案：`hl_price.py` 遍历 perpDexs，按日成交额 / OI 选盘；其余盘列出并标 stale；OI=0 或美股非交易时段输出 price_caveat。SK Hynix 有 SKHX（本地股）与 SKHY（ADR）两个盘，别名默认用 SKHX。

## ISS-006 — SEC XBRL 的 capex 概念因公司而异 [resolved]

- 日期：2026-10-06
- 现象：AMZN 的 `PaymentsToAcquirePropertyPlantAndEquipment` 只到 2017 年，导致 capex 序列停在 2017。
- 根因：AMZN 后来改用 `PaymentsToAcquireProductiveAssets`。
- 方案：`sec_facts.py` 在候选概念里选最近一期最新的那个，并在输出里注明所用概念。

