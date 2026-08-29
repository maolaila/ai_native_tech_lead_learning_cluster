# 模块 07：RabbitMQ 与可靠异步处理

> **所属模块：** 07 Messaging
> **本文用途：** 理解异步价值、消息丢失与重复，并让业务在重试和崩溃条件下仍正确。
> **前置知识：** 事务、测试、Redis
> **建议投入：** 3～4 周

---

同步调用简单，但邮件、积分、统计会把延迟和故障传播到订单。消息队列可解耦、削峰和隔离非核心失败，同时引入最终一致、重复、乱序、积压和运维成本。

文件：

1. [`01_同步异步与事件边界.md`](01_同步异步与事件边界.md)
2. [`02_Exchange_Queue_Routing.md`](02_Exchange_Queue_Routing.md)
3. [`03_Confirm_Ack_Retry_DLQ.md`](03_Confirm_Ack_Retry_DLQ.md)
4. [`04_幂等与Outbox.md`](04_幂等与Outbox.md)
5. [`05_消息契约_顺序与积压.md`](05_消息契约_顺序与积压.md)
6. [`06_实操与验收.md`](06_实操与验收.md)

核心结论：RabbitMQ 提供传递机制，不自动保证业务只执行一次。完整方案依赖事务、Outbox、Confirm、Ack、幂等、Unique、DLQ 和可观测性。
