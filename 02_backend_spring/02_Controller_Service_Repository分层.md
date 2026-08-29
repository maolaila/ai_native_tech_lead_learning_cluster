# Controller、Service、Repository 分层

> **所属模块：** 02 Backend
> **本文用途：** 用职责和依赖方向控制变化，而不是仅把代码拆成多个目录。
> **前置知识：** IoC / DI
> **建议投入：** 阅读 3 小时，重构 5 小时

---

## 一、Controller

负责 HTTP 世界：

- Route；
- Path/Query/Header/Body；
- 触发 Validation；
- 取得认证主体；
- 调用 Use Case；
- 转成 HTTP Response。

不负责：折扣、库存、状态机、事务。

胖 Controller：

```java
@PostMapping("/orders")
Order create(Request req) {
    var product = productRepository.findById(req.productId()).orElseThrow();
    product.setStock(product.getStock() - req.quantity());
    productRepository.save(product);
    return orderRepository.save(...);
}
```

问题：HTTP、业务和数据混在一起；难复用、难测试、事务不清楚。

## 二、Application Service

负责一个业务用例的编排：

```text
读取用户和商品
→ 执行业务规则
→ 扣库存
→ 保存订单
→ 写事件
→ 返回结果
```

它通常是事务入口，但不应成为所有逻辑的垃圾桶。复杂稳定规则应放领域对象/Domain Service。

## 三、Domain

表达业务概念和不变量：

```java
order.cancel();
coupon.applyTo(orderTotal, userId, now);
inventory.reserve(quantity);
```

领域方法比任意 Setter 更安全。

## 四、Repository / Mapper

负责持久化：查询、保存、删除、锁定。

不应决定：权限、折扣、通知、HTTP 格式。

`Mapper` 可能指 MyBatis 数据访问，也可能指对象映射，项目中要明确命名。

## 五、依赖方向

```text
API → Application → Domain
                     ↑
Infrastructure → Repository Interface
```

领域层不应依赖 `HttpServletRequest`、Controller 或具体数据库 Client。

## 六、按业务模块组织

优于全局大目录：

```text
order/
  api/
  application/
  domain/
  infrastructure/
product/
  ...
```

好处：相关上下文聚集；模块边界可见；AI 搜索更准确；跨模块依赖容易审查。

## 七、跨模块调用

Order 不应直接访问 Product 的内部 Repository。定义稳定能力：

```text
ProductCatalogPort.getSellableProducts(...)
InventoryPort.reserve(...)
```

这不是要求复杂 DDD，而是防止所有模块穿透数据库细节。

## 八、过度分层

简单一行查询不需要 12 个类。判断：

- 是否有业务规则？
- 是否跨数据修改？
- 是否需要事务？
- 是否会复用？
- 是否是稳定边界？

架构目标是控制复杂度，不是制造样板。

## 九、AI Guardrail

```text
Controller 不得直接依赖 Repository。
Controller 不得修改 Entity 状态。
Repository 不得发送邮件或调用支付。
跨模块访问必须经过公开接口。
新增事务入口必须说明边界和失败方式。
```
