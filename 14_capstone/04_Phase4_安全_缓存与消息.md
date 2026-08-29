# Phase 4：认证授权、安全、Redis 与 RabbitMQ

> **所属模块：** 14 Capstone
> **本文用途：** 加入跨实例状态和异步流程，同时保持安全和数据权威。
> **前置知识：** Phase 3、安全/Redis/MQ
> **建议投入：** 5～7 周

---

## Auth/Security

选择 Session/JWT/OIDC；USER/ADMIN/SUPPORT；对象级订单权限；XSS/CSRF/SQLi/SSRF/Mass Assignment 测试；Secret Scan；审计。

## Redis

商品 Cache Aside、TTL/随机、Null、失效；下单读权威价；登录限流；Redis 停机降级；指标。

## RabbitMQ

OrderCreated→Notification/Points；Outbox；Confirm；Ack 后置；Retry/DLQ；processed_messages/业务 Unique 幂等。

## 故障

- Redis 过期热点；
- Redis 停机；
- RabbitMQ 停机；
- Publisher Confirm 丢；
- Consumer 提交后 Ack 前崩溃；
- 同 Event 20 次；
- 毒消息 DLQ；
- 旧 Schema 消息。

## 数据正确性

DB 是订单、库存、金额、权限和幂等最终事实。缓存和 Queue 故障不能破坏核心提交。

## 输出

Security Matrix、Cache ADR、Messaging ADR、Event Contract、DLQ Runbook、Failure Reports。
