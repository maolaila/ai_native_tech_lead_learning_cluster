# 测试策略

- Unit：Money、状态机、优惠边界、签名等纯规则。
- Integration：Testcontainers PostgreSQL + 真实 Flyway，验证事务、约束、Mapping 和并发。
- API：认证、校验、401/403/409、错误结构与幂等契约。
- Messaging：Outbox 领取、重投、消费者去重和 DLQ。
- MCP：路径穿越、写 SQL、任意命令和 Prompt Injection。
- Architecture：Controller 不依赖 Repository；Domain 不依赖 Spring/JPA。

历史 Bug 必须先由失败测试复现，再修复并永久保留。覆盖率只表示执行过，不能替代业务断言。
