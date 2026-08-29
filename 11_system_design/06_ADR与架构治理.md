# ADR、架构规则与治理

> **所属模块：** 11 System Design
> **本文用途：** 让关键决策可追溯、可自动检查，并避免架构只存在资深程序员脑中。
> **前置知识：** 架构设计
> **建议投入：** 阅读 4 小时，写作 4 小时

---

## 一、ADR

```markdown
# ADR-007：订单使用模块化单体与 PostgreSQL

Status: Accepted
Context
Decision
Alternatives
Consequences
Validation
Revisit Trigger
```

记录“为什么”，不是复制最终架构图。

## 二、何时写

数据库、认证、缓存、消息、模块边界、公共 API、Cloud、Migration、AI 权限、高风险依赖。

不必为每个变量写 ADR。

## 三、Decision 包含代价

“选择 Redis”不完整。要写收益、失败方式、一致性、监控、退出策略和重审条件。

## 四、Architecture as Code

可自动检查：

- Controller 不依赖 Repository；
- Domain 不依赖 Spring Web/JPA；
- Order 不直接访问 Inventory Repository；
- Migration 只能追加；
- Payment 修改需要 Code Owner；
- API Contract 不破坏。

## 五、Fitness Functions

持续验证架构特性：模块依赖、启动时间、Build 时间、P99、Error Budget、敏感依赖、镜像大小、恢复测试。

## 六、文档新鲜度

文档有 Owner、关联代码、CI 检查关键链接、变更 PR 同时更新。自动生成事实（OpenAPI/Schema），人工维护原因和约束。

## 七、Tech Radar

Adopt/Trial/Assess/Hold，防止每个项目自由选栈。Trial 需要实验范围和评估标准。

## 八、Review 层次

1. 需求和不变量；
2. 模块/数据边界；
3. 失败和恢复；
4. 安全；
5. 验证和可观测性；
6. 运维和成本；
7. 实现细节。

不要一开始只争命名和代码格式。

## 九、AI 友好

ADR、Rules、Glossary 和 Module Map 应短、明确、可检索，示例包含允许与禁止。它们将成为 Coding Agent 的约束输入。
