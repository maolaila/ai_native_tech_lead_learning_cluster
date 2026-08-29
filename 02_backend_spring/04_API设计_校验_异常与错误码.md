# API 设计、校验、异常与错误码

> **所属模块：** 02 Backend
> **本文用途：** 建立可预测、可测试、可演进的 HTTP 契约。
> **前置知识：** DTO 与分层
> **建议投入：** 阅读 4 小时，编码 5 小时

---

## 一、资源设计

```http
GET    /api/products
GET    /api/products/{id}
POST   /api/products
PATCH  /api/products/{id}
DELETE /api/products/{id}
```

业务动作：

```http
POST /api/orders/{id}/cancellation
```

比允许客户端任意 `PATCH status=CANCELLED` 更清楚。

## 二、分页、筛选、排序

```http
GET /api/orders?status=PAID&page=0&size=20&sort=createdAt,desc
```

Offset 简单、可跳页；大 Offset 可能慢。Cursor 适合连续滚动，但实现和契约更复杂。按业务选择。

## 三、三层校验

1. 前端：用户体验；
2. 后端：不信任请求；
3. 数据库：最终完整性。

格式校验：`@NotBlank`、`@Positive`。

业务校验：优惠券属于用户、订单可取消、库存足够。

数据库约束：Unique、Not Null、Foreign Key、Check。

## 四、错误结构

```json
{
  "code": "ORDER_NOT_CANCELLABLE",
  "message": "当前状态不允许取消",
  "traceId": "abc...",
  "details": {"orderId":"123","status":"PAID"}
}
```

前端用 `code` 分支，不解析中文 Message。

## 五、Global Exception Handler

统一：

- 异常到 HTTP Status；
- 业务错误码；
- 日志级别；
- 敏感信息脱敏；
- traceId。

500 不把堆栈返回客户端；服务端保留完整诊断。

## 六、幂等

创建订单或支付：

```http
Idempotency-Key: ...
```

同 Key + 同 Request：返回第一次结果。

同 Key + 不同 Request：409，防止错误复用。

网络超时只说明客户端没收到响应，不能说明服务端未成功。

## 七、版本兼容

破坏性变更：删字段、改类型、改枚举语义、改 Status、改权限、改默认排序。

策略：兼容新增、弃用周期、Contract Test；必要时新版本并行。

## 八、反模式

- 所有接口 POST；
- 所有结果 200；
- 客户端传最终金额；
- 直接返回 Entity；
- 每个 API 分页格式不同；
- 错误码随意创建；
- 没有重复请求语义。
