# Phase 7：Rules、Golden Path、MCP 与新人对照实验

> **所属模块：** 14 Capstone
> **本文用途：** 把项目经验转化为可复用的软件生产体系并量化组织价值。
> **前置知识：** Phase 6、AI Engineering
> **建议投入：** 4～8 周

---

## Knowledge

Architecture、Glossary、Module/Owner、Domain Rules、API/Schema、Testing/Security/Deploy/Observability、Runbooks、ADR。

## Rules

15 条以上；8 条 CI 自动执行；有 Severity、例外和 Owner。

## Golden Paths

`create-feature`、`fix-production-bug`、可选 `add-database-field`、`investigate-incident`。

## MCP

只读优先：知识、Schema、Migration Check、Test、CI Failure、Logs/Trace/Health。生产只读，结果脱敏，Tool Contract、Timeout、审计和权限。

## Eval

至少 30 Task/Hidden Checks；常规、测试、DB、安全、可靠、Debug、架构。记录基线。

## 新人实验

选择 4 个同等任务：

```text
A 通用 Agent
B + Rules
C + Golden Path
D + MCP/Eval
```

记录完成时间、Requirement、Hidden Test、架构/安全违规、Review、返工、成本和新人理解。

## 最终报告

说明哪些能力真正提高、哪些 Tool 无价值、误报和风险、下一阶段路线。不要只展示一次成功录像。
