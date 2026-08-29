# API 与契约测试

> **所属模块：** 03 Testing
> **本文用途：** 验证路由、序列化、校验、认证、错误结构和客户端兼容。
> **前置知识：** 后端/API 基础
> **建议投入：** 阅读 3 小时，编码 5 小时

---

## 一、API 层独有风险

Service 测试通过仍可能：

- Route 错；
- JSON 字段绑定错；
- Validation 未触发；
- Status 错；
- Filter/Security 错；
- Exception Handler 错；
- 时间/金额序列化变了。

## 二、Mock Web 与 Real Port

MockMvc/WebTestClient 快、适合 Controller Slice；Random Port 更接近真实 HTTP。按目标使用两者。

## 三、验证范围

```text
Method / Path
Status / Header / Content-Type
Request / Response Schema
Validation
Authentication
Authorization
Error Code / traceId
Idempotency
Pagination
Backward Compatibility
```

## 四、权限

至少：无凭证、无效凭证、本人、他人、Admin。只验证 Role 不足以覆盖对象级权限。

## 五、Contract

OpenAPI 可生成文档和客户端，也可做破坏性变更检查。但自动生成契约仍需 Review。

字段从字符串金额改成数字、枚举语义变化，可能破坏客户端。

## 六、幂等 API

测试：

- 同 Key + 同 Body；
- 同 Key + 不同 Body；
- 第一次成功但客户端没收到；
- 并发同 Key；
- Key 过期策略。

## 七、练习

为 `POST /orders` 覆盖 201、400、401、403、404、409、500、统一错误结构、内部字段不泄露和幂等。
