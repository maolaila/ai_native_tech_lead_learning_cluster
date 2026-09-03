# Java 后端阅读语法速查

这份说明不是完整 Java 教程，而是让你在阅读本项目时，不必因为一个语法点立刻跳到外部资料。

---

## 一、`package`

```java
package com.example.minicommerce.order.application;
```

大白话：

> 这个类属于哪个包，也就是代码中的“文件分组和命名空间”。

包名通常能看出模块和层次：

```text
order          订单模块
application    应用服务层
```

---

## 二、`import`

```java
import java.util.UUID;
import org.springframework.stereotype.Service;
```

大白话：

> 告诉当前文件后面会使用哪些其他类。

`java.*` 通常来自 Java 标准库；`org.springframework.*` 来自 Spring；`com.example.minicommerce.*` 来自本项目。

### `import xxx.*`

表示导入某个包下可见的多个类型。真实项目中明确导入具体类通常更容易阅读，但格式化工具可能会根据规则整理导入。

---

## 三、`class`

```java
public class CreateOrderService {
}
```

大白话：

> 定义一种对象，它可以拥有字段和方法。

`CreateOrderService` 是类名。

---

## 四、`interface`

```java
public interface PaymentGateway {
    PaymentResult pay(PaymentCommand command);
}
```

大白话：

> 先规定“需要提供什么能力”，但不一定在这里写具体怎样完成。

真实支付实现、测试用假实现，都可以遵守同一个接口。

这让业务代码依赖“能力”，而不是绑死某一家支付平台。

---

## 五、`record`

```java
public record InventoryView(
        Long productId,
        int available,
        int reserved,
        long version) {
}
```

大白话：

> 一种主要用来装数据的简洁类型。

Java 会自动生成：

- 构造器；
- 读取字段的方法；
- `equals()`；
- `hashCode()`；
- `toString()`。

读取字段时通常写：

```java
view.productId()
```

而不是传统 JavaBean 的：

```java
view.getProductId()
```

`record` 适合 DTO、配置和事件数据，但不代表所有业务对象都应该写成 record。

---

## 六、`enum`

```java
public enum OrderStatus {
    PENDING_PAYMENT,
    PAID,
    CANCELLED
}
```

大白话：

> 一个只能从固定选项中选择的类型。

比用任意字符串更安全，因为代码不能随便写出一个不存在的状态。

---

## 七、字段

```java
private final InventoryService inventory;
```

这是一项对象内部保存的数据。

- `private`：只有当前类内部能直接访问；
- `final`：构造完成后，这个字段不能再指向另一个对象；
- `InventoryService`：字段类型；
- `inventory`：字段名。

---

## 八、构造器

```java
public CreateOrderService(InventoryService inventory) {
    this.inventory = inventory;
}
```

大白话：

> 创建 `CreateOrderService` 时，必须把它依赖的 `InventoryService` 传进来。

`this.inventory` 表示当前对象的字段；右边的 `inventory` 是构造器参数。

在 Spring 项目中，这叫构造器注入。

### 为什么不在字段上直接 `new`

```java
private final InventoryService inventory = new InventoryService(...);
```

这种写法会让类自己负责创建复杂依赖，不方便测试和替换。交给 Spring 组合更合适。

---

## 九、方法

```java
public OrderResponse create(Long userId, CreateOrderRequest request) {
    // 方法内容
}
```

拆开看：

- `public`：其他类可以调用；
- `OrderResponse`：返回类型；
- `create`：方法名；
- 圆括号里：需要的参数；
- 花括号里：实际执行步骤。

---

## 十、访问修饰符

| 写法 | 通俗含义 |
|---|---|
| `public` | 其他包中的代码也可以使用 |
| `protected` | 当前类、子类以及同包代码可以使用 |
| 不写 | 只有同一个包中的代码可使用 |
| `private` | 只有当前类内部可使用 |

不要为了“方便”把所有内容都改成 `public`。可见范围越小，代码越不容易被随意依赖。

---

## 十一、`static`

```java
private static final String PREFIX = "MC-";
```

大白话：

> 这项内容属于类本身，而不是每一个对象各自保存一份。

常用于常量和不依赖对象状态的工具方法。

---

## 十二、`final`

### 放在字段上

```java
private final Clock clock;
```

字段初始化后不能再指向另一个 `Clock`。

### 放在局部变量上

表示变量赋值后不再重新赋值。

### 放在类上

表示不能再继承这个类。

`final` 不代表对象内部所有内容都绝对不可变。

---

## 十三、`this`

```java
this.clock = clock;
```

`this` 表示“当前这个对象”。当字段名和参数名相同时，用它区分。

---

## 十四、`if / else`

```java
if (quantity <= 0) {
    throw new IllegalArgumentException("数量必须大于 0");
}
```

大白话：

> 条件成立时，执行花括号中的代码。

本项目关键代码统一建议保留花括号，即使里面只有一行，这样初学者更容易看到代码块范围，后续修改也更安全。

---

## 十五、`for`

```java
for (OrderLineRequest line : request.items()) {
    // 逐项处理订单商品
}
```

大白话：

> 把集合中的每一项依次取出来处理。

---

## 十六、`return`

```java
return OrderMapper.view(order, items);
```

大白话：

> 结束当前方法，并把结果返回给调用方。

---

## 十七、`throw`

```java
throw new BusinessException(ErrorCode.ORDER_EMPTY, "订单不能为空");
```

大白话：

> 当前流程不能继续，抛出一个异常交给上层处理。

项目中的全局异常处理器会把部分异常转换成统一 JSON 错误响应。

---

## 十八、`try / catch / finally`

```java
try {
    gateway.pay(command);
} catch (TimeoutException exception) {
    // 处理超时
} finally {
    // 无论成功失败都会执行
}
```

- `try`：尝试执行可能失败的代码；
- `catch`：捕获指定异常并处理；
- `finally`：不管成功失败都执行，常用于释放资源。

不要为了“让程序不报错”而捕获所有异常后什么都不做。那会把真实问题隐藏起来。

---

## 十九、异常类型

### Checked Exception

编译器要求显式处理或继续声明抛出，例如部分 I/O 异常。

### Runtime Exception

运行时异常，不要求每层都声明。本项目业务异常通常属于这一类，便于事务回滚和统一处理。

### 业务异常

```java
BusinessException
```

表示用户操作或当前业务状态不允许继续，例如库存不足、订单不存在。

它与程序 Bug 不完全相同。

---

## 二十、泛型 `<T>`

```java
List<OrderEntity>
Optional<UserEntity>
Page<ProductResponse>
```

尖括号说明容器里装的是什么类型。

例如：

```java
List<OrderEntity>
```

表示“装着多个 `OrderEntity` 的列表”。

---

## 二十一、`List`

**大白话：**有顺序、可以有重复项的集合。

```java
List<OrderItemEntity> items
```

---

## 二十二、`Set`

**大白话：**不允许重复项的集合。

适合表示唯一 ID 集合等。

---

## 二十三、`Map`

```java
Map<Long, Integer> quantities
```

大白话：

> 通过一个 Key 找到一个 Value。

上例中：

```text
商品 ID → 购买数量
```

---

## 二十四、`Optional`

```java
Optional<OrderEntity> order
```

大白话：

> 这个查询结果可能存在，也可能不存在。

常见处理：

```java
repository.findById(id)
        .orElseThrow(() -> new BusinessException(...));
```

意思是：找到就返回；找不到就抛出指定异常。

### 常见误区

不要在 Entity 字段和所有方法参数中机械使用 `Optional`。它主要适合表达方法返回值“可能没有”。

---

## 二十五、Lambda 表达式 `->`

```java
item -> item.getPrice()
```

大白话：

> 给定左边的参数，执行右边的处理。

另一例：

```java
() -> new BusinessException(...)
```

表示没有输入参数，执行时创建一个异常。

---

## 二十六、Stream

```java
items.stream()
        .map(Item::getPrice)
        .reduce(BigDecimal.ZERO, BigDecimal::add);
```

Stream 是对集合进行连续处理的一种写法。

上例可以读成：

```text
把商品列表变成流
→ 取出每项价格
→ 从 0 开始累加
```

### 常见操作

- `filter`：只保留满足条件的项；
- `map`：把每项转换成另一种值；
- `sorted`：排序；
- `toList`：收集成列表；
- `anyMatch`：是否至少有一项满足条件；
- `reduce`：把多项合并成一个结果。

Stream 很方便，但链条太长会难读。业务步骤复杂时，普通 `for` 循环反而更清楚。

---

## 二十七、方法引用 `::`

```java
BigDecimal::add
InventoryService::view
```

它是 Lambda 的简写。

```java
BigDecimal::add
```

大致等同于：

```java
(left, right) -> left.add(right)
```

---

## 二十八、`var`

```java
var now = clock.instant();
```

大白话：

> 让编译器根据右边推断变量类型。

`var` 不是动态类型，类型在编译时仍然确定。

如果右边表达式很复杂，写出明确类型通常更容易阅读。

---

## 二十九、`UUID`

```java
UUID orderId = UUID.randomUUID();
```

大白话：

> 生成一个非常难重复的标识符。

适合分布式环境创建业务 ID，但它不是绝对安全密钥，也不等于随机 Token。

---

## 三十、`BigDecimal`

金额不要使用 `double`：

```java
BigDecimal total
```

原因是二进制浮点数不能精确表示部分十进制小数，可能出现：

```text
0.1 + 0.2 ≠ 精确的 0.3
```

项目使用 `BigDecimal` 并明确保留小数位和舍入方式。

### 常见操作

```java
price.multiply(quantity)
subtotal.subtract(discount)
amount.setScale(2, RoundingMode.HALF_UP)
```

不要用 `==` 比较 `BigDecimal`。

---

## 三十一、`Duration`

```java
Duration readTimeout
```

大白话：

> 表示一段时间，例如 2 秒、5 分钟。

Spring 配置中可写：

```yaml
read-timeout: 5s
```

比用裸数字 `5000` 更不容易搞错单位。

---

## 三十二、`Instant`

```java
Instant createdAt
```

大白话：

> 表示时间线上的一个明确时刻，通常按 UTC 保存。

---

## 三十三、`Clock`

```java
private final Clock clock;
```

大白话：

> 一个可以提供“当前时间”的对象。

为什么不用到处直接写 `Instant.now()`：测试时可以把 `Clock` 换成固定时间，使测试结果稳定。

---

## 三十四、`Page` 和 `Pageable`

```java
Page<ProductResponse> list(Pageable pageable)
```

- `Pageable`：调用方希望查询第几页、每页多少条、怎样排序；
- `Page`：返回当前页内容和总页数等信息。

分页可以避免一次把几十万条数据全部读进内存。

---

## 三十五、继承 `extends`

```java
public class CartItemEntity extends BaseEntity {
}
```

大白话：

> `CartItemEntity` 继承了 `BaseEntity` 中可继承的字段和行为。

本项目用它统一创建时间和更新时间等基础字段。

不要为了复用几行代码就建立很深的继承层次。

---

## 三十六、实现 `implements`

```java
public class FakePaymentGateway implements PaymentGateway {
}
```

大白话：

> 这个类承诺提供 `PaymentGateway` 接口规定的能力。

---

## 三十七、注解 `@...`

注解是给框架或工具看的标签。

完整说明见：[Spring 与 Java 注解小白词典](SPRING-JAVA-ANNOTATIONS.md)。

---

## 三十八、Javadoc

```java
/**
 * 创建订单。
 *
 * @param request 下单请求
 * @return 创建后的订单
 */
```

`/** ... */` 是可以被 IDE 和文档工具识别的说明注释。

本项目的关键类和方法会说明：

```text
作用
为什么
对应文档
```

---

## 三十九、项目中先不要深挖的语法

第一遍遇到以下内容，可以先知道用途，不必研究底层：

- 反射；
- 动态代理；
- AOP 字节码增强；
- 注解处理器；
- 类加载器；
- JVM 内存模型全部细节；
- Hibernate Session 内部状态。

先把请求链和业务规则看懂，再逐步深入。

## 四十、阅读一行 Java 的固定顺序

例如：

```java
private final InventoryService inventory;
```

按顺序读：

```text
可见范围：private
是否可重新赋值：final
类型：InventoryService
名字：inventory
```

例如：

```java
public Optional<OrderEntity> findById(UUID id)
```

按顺序读：

```text
谁能调用：public
返回什么：可能存在也可能不存在的 OrderEntity
方法名：findById
需要什么参数：UUID 类型的 id
```

这样拆开读，比整行一起猜更容易。
