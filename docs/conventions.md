---
last_updated: 2026-06-26
status: active
owner: kumata
---

# 项目约定

## 文档

- `SKILL.md` 只放触发、路由和高层执行约束；长流程放到 `knowledge/`。
- 市场专属细则放到 `knowledge/markets/`，通用投资框架放到 `knowledge/frameworks/`。
- `docs/plan.md` 是活跃计划；完成历史迁入 `docs/plan-archive.md`。
- 不在 README 里重复大段 workflow，README 只保留定位、安装、快速使用和验证命令。

## Skill 内容

- frontmatter 只保留 `name` 和 `description`，确保跨平台兼容。
- 所有路径使用仓库相对路径，假设 agent 工作目录是 skill 根目录。
- 不把第三方付费课程逐章笔记作为主流程依赖；主流程只依赖可分发的综合框架。
- 不内置私人账号、访问令牌、外发频道 ID、私聊 ID、代理地址。

## Python

- 脚本优先使用标准库；确需依赖时在 README 写明。
- 校验器应给出可操作错误信息，退出码约定：`0` 通过、`1` 校验失败、`2` 用法或解析错误。
- 文件读写使用 UTF-8。

## 报告输出

- `reports/` 与 `examples/` 是运行期目录，默认不入库。
- 文件名带标的和日期：`<ticker_or_code>_<YYYY-MM-DD>.md|yaml`。
- A 股报告必须含数据核实日期和主要来源。
- 美股/海外 thesis 必须通过 4 维校验；A 股报告必须通过结构校验。

## 变更纪律

- 只改与当前 skill 行为相关的文件。
- 改市场流程时同步更新 `SKILL.md`、对应 `knowledge/` 文件、README 和校验器。
- 新增数据源或交付渠道前先写隐私与失败模式。
