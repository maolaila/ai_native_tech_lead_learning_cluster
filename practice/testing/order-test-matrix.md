# Order Test Matrix

| ID | Category | Given | When | Then | Layer |
|---|---|---|---|---|---|
| O-001 | Happy | 可售、库存 2 | 买 1 | 订单创建、库存 1 | Integration/API |
| O-002 | Boundary | quantity=1 | 下单 | 成功 | Unit/API |
| O-003 | Invalid | quantity=0 | 下单 | 400/ORDER_ITEM_INVALID | API |
| O-004 | Invalid | 空 items | 下单 | 400/ORDER_EMPTY | Unit/API |
| O-005 | Product | 商品不存在 | 下单 | 404 | Integration/API |
| O-006 | Product | 商品下架 | 下单 | 409 | Unit/Integration |
| O-007 | Price | 前端提交伪造金额 | 下单 | 后端忽略并重算 | API/Integration |
| O-008 | Snapshot | 下单后改商品名价 | 查历史订单 | 快照不变 | Integration/E2E |
| O-009 | Stock | 库存 0 | 下单 | 409、无订单 | Integration |
| O-010 | Transaction | 订单写后库存失败 | 下单 | 全部回滚 | Integration |
| O-011 | Idempotency | 相同 Key/Body | 两次下单 | 一个订单 | API/Concurrency |
| O-012 | Conflict | 相同 Key/不同 Body | 第二次 | 409 | API |
| O-013 | Concurrency | stock=1 | 20 同时 | 成功 <=1、库存 0 | Integration |
| O-014 | Auth | 未登录 | 下单 | 401 | API/E2E |
| O-015 | Ownership | Alice 查 Bob 订单 | GET | 403/404 | API |
| O-016 | State | 已支付订单 | 取消 | 拒绝或退款流程 | Unit/API |
| O-017 | Duplicate | 已取消订单 | 再取消 | 幂等/明确冲突 | Unit/API |
| O-018 | MQ | Broker 挂 | 下单 | 订单成功、Outbox Pending | Integration |
| O-019 | Message | 同 eventId 20 次 | 消费 | 积分一次 | Integration |
| O-020 | Observability | 创建失败 | 调查 | 有 traceId/order context | API/Manual |

扩展时加入优惠券、支付、退款、时区、Migration 兼容、负载和恢复。
