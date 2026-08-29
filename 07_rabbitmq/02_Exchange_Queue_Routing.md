# Exchange、Queue、Binding 与 Routing

> **所属模块：** 07 Messaging
> **本文用途：** 理解 RabbitMQ 路由拓扑，区分广播和竞争消费。
> **前置知识：** 异步边界
> **建议投入：** 阅读 4 小时，配置 4 小时

---

## 模型

```text
Producer → Exchange → Binding → Queue → Consumer
```

Exchange 让 Producer 表达消息类型，而不是写死 Consumer。

## Exchange

- Direct：Routing Key 精确匹配，适合命令；
- Topic：模式匹配，适合 `order.created.v1`；
- Fanout：广播所有绑定 Queue；
- Headers：按 Header，当前项目少用。

## 广播与扩容

三个业务都要收到，应是三个独立 Queue：

```text
order.created
├─ notification-q
├─ points-q
└─ analytics-q
```

同一个 Queue 上三个 Consumer 是竞争消费，一条消息通常只给其中一个，用于水平扩容。

## Durable / Persistent

Durable 保留拓扑定义；Persistent 提示消息持久化，但不等于绝对零丢失，仍需 Confirm 和正确 Broker 配置。

## 命名

```text
Exchange: commerce.order.events
Queue: notification.order-created.v1
DLQ: notification.order-created.v1.dlq
Routing Key: order.created.v1
```

## VHost 与权限

dev/staging/prod 隔离；应用账号只能访问需要的 Exchange/Queue；本地不能误连生产。

## Prefetch

太大导致单 Consumer 囤消息、负载不均和失败重投多；太小吞吐不足。通过处理时间、积压和资源测量调整。

## 声明

拓扑应版本化、幂等、可审计；避免不同应用用冲突参数声明同名 Queue。
