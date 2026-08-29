# 长期项目：Mini Commerce

> **所属模块：** 00 起步
> **本文用途：** 定义贯穿所有模块的业务系统，使所有知识点落在同一上下文中。
> **前置知识：** 阅读总路线
> **建议投入：** 首次设计 2～3 小时，之后持续演进

---

## 一、项目定位

项目不是要做成完整淘宝，而是提供足够真实的工程复杂度：

```text
Identity      用户、角色、权限
Catalog       商品、分类、上下架
Inventory     库存、预留、恢复
Cart          购物车
Order         订单、订单项、状态机
Promotion     优惠券
Payment       模拟支付和重复回调
Notification  邮件/站内通知任务
Audit         操作审计
```

前端使用你最熟悉的框架；后端采用 Java + Spring Boot；数据库 PostgreSQL；之后依次加入 Redis、RabbitMQ、Docker、CI/CD、Prometheus、Grafana、OpenTelemetry 和 MCP。

## 二、第一阶段模块边界

建议模块化单体：

```text
backend/src/main/java/.../
├─ identity/
├─ catalog/
├─ inventory/
├─ cart/
├─ order/
├─ promotion/
├─ payment/
├─ notification/
├─ audit/
└─ shared/
```

每个模块内部再按：

```text
api/
application/
domain/
infrastructure/
```

### 为什么不一开始微服务

模块化单体：

- 本地启动和调试简单；
- 可以使用本地事务；
- 部署成本低；
- 仍能训练边界与依赖方向；
- 将来是否拆分由真实耦合和负载决定。

一开始拆 10 个服务，会同时引入网络失败、服务发现、分布式事务、版本兼容和链路追踪，把学习重点带偏。

## 三、核心不变量

1. 库存不能小于 0；
2. 已取消订单不能支付；
3. 同一优惠券不能重复使用；
4. 订单金额由服务端计算，不能信任前端；
5. 订单项保存成交时名称与价格快照；
6. 重复支付回调不能重复变更业务；
7. 权限不能只靠前端隐藏按钮；
8. 核心状态变化可审计；
9. 数据库修改必须有 Migration；
10. 历史 Bug 修复后必须有 Regression Test。

## 四、一个生动例子：商品快照

用户下单时商品叫“键盘 A”，价格 8,000 日元。三天后管理员改名为“键盘 B”，价格 9,500 日元。

若订单详情每次 JOIN 当前商品表，历史订单会显示新的名称和价格，破坏成交事实。因此 `order_items` 保存：

```text
product_id
product_name_snapshot
unit_price_snapshot
quantity
```

这里的重复不是坏设计，而是表达“历史事实”。

## 五、订单状态机

```text
PENDING_PAYMENT → PAID → FULFILLING → COMPLETED
       │             │
       └→ CANCELLED  └→ REFUNDING → REFUNDED
```

不允许任何代码直接 `setStatus`。使用：

```java
order.cancel();
order.markPaid(paymentId);
order.requestRefund();
```

领域方法负责检查合法转换。

## 六、仓库建议

```text
mini-commerce/
├─ frontend/
├─ backend/
├─ e2e/
├─ docs/
│  ├─ architecture.md
│  ├─ domain-model.md
│  ├─ api-design.md
│  ├─ database-design.md
│  ├─ testing-strategy.md
│  └─ adr/
├─ infra/
├─ scripts/
└─ .github/workflows/
```

## 七、阶段演进

1. User、Product、Order CRUD；
2. Unit / Integration / API / E2E；
3. Index、Transaction、Lock、Migration；
4. Session/JWT、RBAC、安全；
5. Redis 缓存与限流；
6. RabbitMQ、Outbox、幂等；
7. Docker、CI/CD、Rollback；
8. Logs、Metrics、Traces、故障演练；
9. Architecture Docs、Rules、Golden Path、MCP、Eval。

最终衡量标准不是页面数量，而是你能解释每个工程决定的原因和失败方式。
