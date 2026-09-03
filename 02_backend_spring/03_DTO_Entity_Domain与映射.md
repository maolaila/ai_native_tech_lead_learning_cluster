# DTO、Entity、Domain 与映射

> **所属模块：** 02 Backend
> **本文用途：** 防止数据库结构、业务规则和 API 契约绑成一个对象。
> **前置知识：** 分层
> **建议投入：** 阅读 3 小时，编码 4 小时

> 注解看不懂时先查：[Spring 与 Java 注解小白词典](../mini-commerce/docs/SPRING-JAVA-ANNOTATIONS.md)。Java `record`、`BigDecimal`、`UUID` 等语法见：[Java 后端阅读语法速查](../mini-commerce/docs/JAVA-SYNTAX-FOR-BACKEND-BEGINNERS.md)。

---

## 一、先用一个比喻区分

```text
Request DTO   客户交给柜台的申请表
Response DTO  柜台交给客户的回执
Entity        仓库里真实保存的记录格式
Domain Model  业务负责人执行规则时使用的业务对象
```

它们有时字段相似，但职责不同，所以不应默认合并成一个类。

## 二、四类模型

### Request DTO

只允许客户端提交的字段：

```java
record CreateProductRequest(
        @NotBlank String name,
        @Positive BigDecimal price,
        @PositiveOrZero int stock) {
}
```

通俗解释：

- `record`：主要用来装数据的简洁 Java 类型；
- `@NotBlank`：名称不能是空字符串或只有空格；
- `@Positive`：价格必须大于 0；
- `@PositiveOrZero`：库存必须大于等于 0。

Request DTO 像白名单：只写在这里的字段才允许由客户端提供。

### Response DTO

只暴露 API 承诺给调用方的字段。

例如用户响应可以包含昵称和角色，但绝不能包含密码哈希、重置 Token 和内部风控备注。

### Entity

Entity 主要表达：

- 对应哪张数据库表；
- 字段对应哪一列；
- 主键是什么；
- 列是否允许为空；
- 记录之间有什么关系；
- 持久化状态怎样变化。

常见注解：

```text
@Entity
@Table
@Id
@GeneratedValue
@Column
```

### Domain Model

Domain Model 主要表达业务行为和不能被破坏的规则。

例如：

```java
order.cancel();
order.markPaid();
```

这些方法应该检查当前状态是否允许变化，而不是让所有调用者随便改字段。

简单 CRUD 时 Entity 与 Domain 可以暂时接近；业务复杂后应有意识分离。

## 三、直接返回 Entity 的风险

User Entity 可能含：

```text
passwordHash
passwordResetToken
riskFlag
internalNote
```

如果直接返回 Entity，一次序列化配置变化就可能把内部字段暴露给前端。

Response DTO 使用白名单思路：明确决定哪些字段可以对外。

## 四、Mass Assignment

Mass Assignment 可以用大白话理解为：

> 把客户端提交的所有字段不加选择地直接塞进 Entity。

攻击者可能提交：

```json
{
  "displayName": "Alice",
  "role": "SUPER_ADMIN"
}
```

如果代码直接绑定 Entity，攻击者可能修改本不允许修改的角色字段。

解决办法：使用专用 Request DTO，再显式把允许字段映射到业务对象。

## 五、数据库结构不等于 API 结构

数据库可能为了约束和查询拆成多张表；API 可以把它们组合成一个方便使用的响应。

反过来，API 中为了展示增加的字段，也不一定要在数据库中一一保存。

因此：

```text
表结构变化 ≠ API 必须变化
API 变化 ≠ 表结构必须完全相同
```

## 六、Value Object

```java
record Money(BigDecimal amount, Currency currency) {
}

record OrderId(UUID value) {
}

record Email(String value) {
}
```

Value Object 可以理解成：

> 不只传一个裸值，还把这个值的业务含义和校验一起装起来。

好处：

- `Money` 不容易和普通数字混淆；
- `OrderId` 不容易误传成 `UserId`；
- Email 校验可以集中；
- 代码更接近业务语言。

## 七、金额和时间

### 金额

- 不使用 `double`；
- 使用 `BigDecimal` 或最小货币单位整数；
- 明确币种；
- 明确保留几位小数；
- 明确舍入方式。

### 时间

- `Instant`：时间线上的明确时刻，适合记录创建时间；
- `LocalDate`：只有日期，例如生日；
- 业务时区：例如每天 00:00 结算时，必须明确按哪个地区时间。

API 通常使用 ISO-8601 格式传递时间。

## 八、映射是什么

映射就是把一种对象转换成另一种对象。

```java
static ProductResponse from(ProductEntity product) {
    return new ProductResponse(
            product.getId(),
            product.getName(),
            product.getPrice());
}
```

显式映射虽然多写几行，但容易看出：

- 哪些字段对外；
- 哪些字段被忽略；
- 金额和时间怎样转换；
- 枚举怎样处理。

可以使用 MapStruct 等工具，但必须审查 Null、Enum、Time、Money、敏感字段和嵌套对象。

## 九、为什么领域对象不公开全部 Setter

下面写法允许任何代码随便改状态：

```java
order.setStatus(COMPLETED);
```

更合理的是：

```java
order.complete();
```

`complete()` 内部可以检查：

```text
当前状态是否允许完成
是否已经支付
是否重复执行
```

这叫保护业务不变量。

## 十、版本兼容

Response DTO 是客户端依赖的契约。

下面变化都可能破坏旧客户端：

- 删除字段；
- 改字段类型；
- 改枚举含义；
- 改默认排序；
- 把原来可为空的字段改成必填。

数据库内部 Migration 不应自动等于 API 破坏。

## 十一、本项目中的对应位置

```text
mini-commerce/backend/src/main/java/com/example/minicommerce/order/api/OrderDtos.java
mini-commerce/backend/src/main/java/com/example/minicommerce/order/infrastructure/OrderEntity.java
mini-commerce/backend/src/main/java/com/example/minicommerce/order/infrastructure/OrderItemEntity.java
mini-commerce/backend/src/main/java/com/example/minicommerce/cart/infrastructure/CartItemEntity.java
mini-commerce/backend/src/main/java/com/example/minicommerce/shared/domain/Money.java
```

## 十二、自测

1. Request DTO、Response DTO 和 Entity 分别解决什么问题？
2. 为什么直接返回 User Entity 可能泄露信息？
3. Mass Assignment 是什么？
4. 为什么金额不用 `double`？
5. 为什么 `order.complete()` 通常比 `setStatus()` 更安全？
6. 为什么历史订单项要保存商品名称和成交价格快照？
