# Golden Path、Skills 与模板

> **所属模块：** 13 AI Engineering
> **本文用途：** 把常见开发任务铺成安全的默认道路，让新人和 AI 少做高风险自由发挥。
> **前置知识：** Rules
> **建议投入：** 阅读 5 小时，制作 8 小时

---

## 一、Golden Path

公司推荐且自动化程度最高的实现路径。开发者可以偏离，但偏离需要理由。

例如“新增后台 CRUD”默认生成：

```text
Module/API/Application/Domain/Infrastructure
Migration
OpenAPI
Validation/Error Code
RBAC
Unit/Integration/API
Frontend list/form
Audit Log
Dashboard metric
Docs/ADR if needed
```

## 二、为什么有效

- 把架构默认化；
- 降低新人记忆负担；
- 统一测试和监控；
- 减少 AI 每次重新发明；
- Review 聚焦业务例外。

## 三、Skill / Workflow Contract

```text
/create-feature
输入：Feature Spec、Module、Actor、Rules、Acceptance
步骤：读取上下文→风险分析→设计→人确认高风险→实现→测试→报告
输出：代码、Migration、Test、Docs、风险、证据
禁止：生产写、删数据、改失败回归测试
```

## 四、模板不是代码复制

模板应包含 Hook 和约束，不固定所有业务。过重脚手架会难升级、形成大量 fork。

## 五、示例驱动

给 Agent：一个高质量 Feature PR、一个错误反例、Review Checklist。具体示例往往比抽象“写好代码”更有效。

## 六、阶段化任务

不要让 Agent 一次“完成整个支付系统”。拆为：Spec→设计→Schema/API→核心领域→持久化→测试→前端→Observability→Review。每阶段有验证和 Stop Point。

## 七、计划先于代码

要求先输出：受影响模块、数据变更、状态/事务、权限、安全、测试层、发布风险。简单改动可轻量，复杂改动必须人审计划。

## 八、完成报告

```markdown
Files Changed
Requirements Covered
Architecture Decisions
DB/API Compatibility
Tests Run + Results
Security Review
Observability
Known Risks
Rollback
Unverified Assumptions
```

## 九、Golden Path 的产品化

有 Owner、版本、文档、Telemetry、用户反馈、升级机制和弃用策略。内部平台也需要产品思维。
