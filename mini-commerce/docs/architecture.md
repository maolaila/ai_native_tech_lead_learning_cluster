# 架构说明

本工程是模块化单体：Identity、Catalog、Inventory、Cart、Promotion、Order、Payment、Notification、Audit 运行在一个 Spring Boot 进程中，但按业务模块和 `api/application/domain/infrastructure` 分隔。

核心同步事务只覆盖 PostgreSQL 内可原子提交的状态；支付等外部副作用在事务外调用。可靠异步使用 Transactional Outbox，RabbitMQ 提供至少一次传递，消费者使用 `processed_messages` 和业务 Unique 保证副作用幂等。

```text
HTTP → Security/RateLimit → Controller → Application Service → Domain/Repository → PostgreSQL
                                               ├→ Redis（可丢展示缓存/限流）
                                               ├→ Outbox → RabbitMQ → Idempotent Consumer
                                               └→ Payment Port（事务外）
```

为什么不拆微服务：当前目标是训练正确边界、事务、测试和运行闭环；没有真实独立伸缩、团队所有权或故障隔离证据时，拆分只会提前引入网络和分布式事务复杂度。
