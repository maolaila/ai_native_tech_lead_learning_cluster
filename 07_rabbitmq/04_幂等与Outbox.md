# 幂等、Transactional Outbox 与重复消息

> **所属模块：** 07 Messaging
> **本文用途：** 闭合数据库与消息双写空窗，并防止重复扣款、重复积分。
> **前置知识：** 事务、Confirm/Ack
> **建议投入：** 阅读 5 小时，实现 8 小时

---

## 一、重复不可避免

Confirm 回包丢、Ack 丢、进程崩溃、用户重试、DLQ 重放都可能重复。不要追求网络“绝对只投一次”，要让副作用幂等。

## 二、Processed Messages

```sql
CREATE TABLE processed_messages (
  consumer_name varchar(100) NOT NULL,
  event_id uuid NOT NULL,
  processed_at timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY(consumer_name,event_id)
);
```

同一事务：插入去重记录→业务副作用→提交→Ack。Unique 冲突表示已经处理。

不能先单独提交去重记录，再做业务，否则业务失败后永远被跳过。

## 三、业务 Unique

每订单只加一次积分：

```sql
CREATE UNIQUE INDEX ux_points_order_reason
ON points_ledger(order_id, reason);
```

比“先查不存在”更能防并发。

## 四、双写

```text
DB 提交订单
→ 进程崩溃
→ 消息没发
```

或先发消息后 DB 回滚，都不正确。

## 五、Outbox

同一 DB 事务：

```text
写 orders
写 outbox_events(PENDING)
提交
```

独立 Publisher 领取 Pending→发送→等待 Confirm→标记 Published。

Outbox 保证业务与待发布记录一起存在，但发布成功、标记前崩溃仍会重发，所以 Consumer 仍需幂等。

完整组合：

```text
Outbox + Confirm + At-least-once + Idempotent Consumer
```

## 六、Outbox 字段

`event_id, aggregate, event_type, schema_version, payload, status, attempt_count, next_attempt_at, last_error, created_at, published_at`。

Pending Partial Index；多 Publisher 可使用 `FOR UPDATE SKIP LOCKED`；已发布事件需归档/清理。

## 七、API 幂等键

保存 Key、Request Fingerprint、Status、Response。相同 Key 不同 Body 返回冲突。

## 八、补偿

跨服务已发生动作不能数据库 Rollback，只能执行业务补偿。当前阶段理解 Saga 概念，不急着上框架。
