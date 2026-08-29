# Phase 1：业务建模、前后端与 CRUD

> **所属模块：** 14 Capstone
> **本文用途：** 建立模块化单体和第一条订单闭环，不加入高级组件。
> **前置知识：** 基础与后端
> **建议投入：** 4～6 周

---

## 范围

User、Product、Inventory、Cart、Order、Admin 最小版。

## 文档先行

- Product Brief；
- Glossary；
- Context/Module Map；
- ER 图；
- Order 状态机；
- API Contract；
- 10 条不变量；
- ADR：模块化单体、PostgreSQL、ID/金额/时间策略。

## Backend

按业务模块，Controller→Application→Domain→Repository；Request/Response DTO；Validation；Global Error；Structured Log；Flyway。

## Frontend

商品列表/详情、购物车、创建订单、订单列表/详情、Admin Product；Loading/Error/Empty；重复提交保护；API Client 和错误码统一。

## 数据

至少 users、roles、products、inventory、carts/cart_items、orders/order_items、idempotency_keys、audit_log。

## 限制

不使用 Redis、MQ、微服务、K8s、真实支付。先证明基础设计。

## 验收 Demo

注册/登录占位或临时用户→浏览→购物车→下单→库存变化→订单详情→Admin 修改商品→历史订单快照不变。

## Evidence

架构图、ER、OpenAPI、Migration、README、Commit History、手工测试记录和已知风险。
