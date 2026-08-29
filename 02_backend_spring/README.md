# 模块 02：Spring Boot 后端工程

> **所属模块：** 02 Backend
> **本文用途：** 从基础 Demo 升级到能设计、实现和 Review 可维护的业务模块。
> **前置知识：** 模块 01
> **建议投入：** 5 周

---

## 核心链路

```text
HTTP Request
→ Controller
→ Application Service
→ Domain
→ Repository / Mapper
→ PostgreSQL
```

重点不是记住名称，而是理解每层职责、依赖方向和失败边界。

## 文件

1. [`01_请求生命周期与IoC_DI.md`](01_请求生命周期与IoC_DI.md)
2. [`02_Controller_Service_Repository分层.md`](02_Controller_Service_Repository分层.md)
3. [`03_DTO_Entity_Domain与映射.md`](03_DTO_Entity_Domain与映射.md)
4. [`04_API设计_校验_异常与错误码.md`](04_API设计_校验_异常与错误码.md)
5. [`05_日志_配置与健康检查.md`](05_日志_配置与健康检查.md)
6. [`06_订单模块案例.md`](06_订单模块案例.md)
7. [`07_实操与验收.md`](07_实操与验收.md)

## 过关表现

只给“实现订单模块”，你能主动定义：业务规则、Request/Response、层次、错误码、事务候选、日志字段和测试轮廓，而不是直接让 AI 生成 Controller。
