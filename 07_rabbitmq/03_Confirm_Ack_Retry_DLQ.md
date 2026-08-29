# Publisher Confirm、Ack、Retry 与 DLQ

> **所属模块：** 07 Messaging
> **本文用途：** 沿消息完整旅程分析丢失点和失败点。
> **前置知识：** RabbitMQ 路由
> **建议投入：** 阅读 5 小时，故障实验 6 小时

---

## 消息旅程

```text
DB 业务变更
→ Producer 序列化/发送
→ Broker 接收/路由/持久化
→ Queue
→ Consumer
→ 本地业务事务
→ Ack
```

## Confirm

覆盖 Producer→Broker。`send()` 没抛异常不等于 Broker 已收到，更不等于 Consumer 成功。

Confirm 失败：记录 eventId、有界重试、超限告警；结合 Outbox 重新投递。

## Ack

覆盖 Broker→Consumer。通常在本地业务事务提交后 Ack。

先 Ack 后处理：业务失败时消息永久丢失。

提交后 Ack 前崩溃：消息会重投，所以 Consumer 必须幂等。

## Retry

瞬时：网络、503、短暂 DB 连接，可重试。

永久：Schema 无法解析、必填缺失，不应无限重试。

使用有上限的指数退避和随机抖动；设置单次 Timeout、最大次数、最终处置。

## Requeue 风险

立即 `requeue=true`：取出→失败→回队→立即再取，形成高速死循环。

## DLQ

不是垃圾桶，必须有：数量/最老年龄告警、Payload/Header、失败原因、次数、eventId/traceId、重放工具、保留策略和人工处理流程。

## 故障点

- DB 成功、消息未发：Outbox；
- Broker 收到、Confirm 丢：Producer 可能重发；
- Consumer 提交、Ack 丢：Broker 重投；
- 先 Ack、后处理失败：永久丢失。

## 指标

Publish/Confirm、Ready、Unacked、Consumer、Redelivery、Retry、DLQ、Oldest Age、Processing Latency。
