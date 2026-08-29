# DTO、Entity、Domain 与映射

> **所属模块：** 02 Backend
> **本文用途：** 防止数据库结构、业务规则和 API 契约绑成一个对象。
> **前置知识：** 分层
> **建议投入：** 阅读 3 小时，编码 4 小时

---

## 一、四类模型

### Request DTO

只允许客户端提交的字段：

```java
record CreateProductRequest(
    @NotBlank String name,
    @Positive BigDecimal price,
    @PositiveOrZero int stock
) {}
```

### Response DTO

只暴露 API 承诺的字段。

### Entity

表达表、列、关系和持久化状态。

### Domain Model

表达业务行为与不变量。

简单 CRUD 时 Entity 与 Domain 可暂时接近；业务复杂后应有意识分离。

## 二、直接返回 Entity 的风险

User Entity 可能含：

```text
passwordHash
passwordResetToken
riskFlag
internalNote
```

序列化配置变化就可能泄露。Response DTO 采用白名单。

## 三、Mass Assignment

直接把 Request 绑定 Entity：

```json
{"displayName":"Alice","role":"SUPER_ADMIN"}
```

攻击者可能修改不允许字段。使用专用 Request DTO。

## 四、DB 结构不等于 API

数据库为约束拆多张表；API 可以返回聚合视图。反之 API 字段也不应迫使数据库一一对应。

## 五、Value Object

```java
record Money(BigDecimal amount, Currency currency) {}
record OrderId(UUID value) {}
record Email(String value) {}
```

好处：语义、集中校验、减少 ID 误传、便于 AI 理解。

## 六、金额和时间

- 金额不用 `double`；使用 BigDecimal 或最小货币单位整数；
- 明确 Currency 和舍入；
- 时间保存明确时间点，API 使用 ISO-8601；
- 区分 Instant、LocalDate 和业务时区。

## 七、映射

显式映射最易读：

```java
static ProductResponse from(Product product) { ... }
```

可使用 MapStruct，但必须 Review Null、Enum、Time、Money、敏感字段和嵌套对象。

## 八、不可变性

DTO 用 `record` 很合适。领域对象不应公开全部 Setter：

```java
order.complete();
```

优于：

```java
order.setStatus(COMPLETED);
```

## 九、版本兼容

Response DTO 是客户端契约。删除字段、改变类型、枚举或默认排序都可能破坏旧客户端。数据库内部迁移不应自动等于 API 破坏。
