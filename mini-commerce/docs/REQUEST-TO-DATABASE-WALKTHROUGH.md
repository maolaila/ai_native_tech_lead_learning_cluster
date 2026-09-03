# 一次创建订单请求：从 HTTP 到数据库的完整走读

这份走读只做一件事：跟踪一条创建订单请求，看它怎样经过 Controller、Service、Repository、数据库和 Outbox。

不要先背类名。先把它当成一次真实办事流程。

---

## 一、调用方发送请求

示例：

```http
POST /api/orders HTTP/1.1
Authorization: Bearer <access-token>
Idempotency-Key: create-order-001
Content-Type: application/json

{
  "items": [
    {"productId": 1, "quantity": 2}
  ],
  "couponCode": "WELCOME10"
}
```

逐项解释：

- `POST /api/orders`：请求创建订单；
- `Authorization`：当前登录用户的凭证；
- `Idempotency-Key`：这次业务操作的唯一编号，用来防止重复下单；
- `Content-Type`：请求体是 JSON；
- `items`：购买哪些商品和数量；
- `couponCode`：准备使用的优惠券。

请求中**没有最终成交金额**。金额必须由后端读取数据库中的商品价格并重新计算，不能相信前端传入的价格。

---

## 二、请求进入 `OrderController`

文件：

```text
backend/src/main/java/com/example/minicommerce/order/api/OrderController.java
```

你会看到类似结构：

```java
@PostMapping
@ResponseStatus(HttpStatus.CREATED)
public OrderResponse create(
        @RequestHeader("Idempotency-Key") String key,
        @Valid @RequestBody CreateOrderRequest request) {
    return createOrderService.create(currentUser.require().id(), key, request);
}
```

### 每个注解的作用

- `@PostMapping`：这个方法接收 POST 请求；
- `@ResponseStatus(CREATED)`：成功时返回 201；
- `@RequestHeader`：从请求头读取幂等键；
- `@RequestBody`：把 JSON 转成 Java 请求对象；
- `@Valid`：先检查请求对象上的基础校验规则。

### Controller 做了什么

```text
读取当前用户
+ 读取幂等键
+ 读取请求 JSON
+ 调用创建订单服务
```

### Controller 没做什么

它不应该在这里：

- 计算价格；
- 扣库存；
- 操作优惠券；
- 直接保存订单；
- 直接调用 Repository。

原因是 Controller 只负责 HTTP 边界，业务规则应该放在应用服务中。

---

## 三、请求对象进入 `CreateOrderService`

文件：

```text
order/application/CreateOrderService.java
```

主方法：

```java
@Transactional
public OrderResponse create(...)
```

`@Transactional` 的通俗含义：

> 这个方法中的关键数据库修改要一起成功；中途失败时一起撤销。

创建订单不是一次简单的 INSERT。它需要同时改变多处数据，所以需要明确事务边界。

---

## 四、第 1 步：检查幂等键

系统先检查：

```text
幂等键是否为空
幂等键是否过长
这个用户是否已经使用过同一个键
```

### 为什么只查数据库还不够

如果两个相同请求同时到达，它们可能同时查到“记录不存在”。所以完整方案还需要：

- 同一个用户和幂等键的并发协调；
- 数据库唯一约束；
- 请求指纹；
- 原结果记录。

### 请求指纹是什么

系统根据商品、数量和优惠券等关键内容计算一个摘要。

```text
相同 Key + 相同指纹 → 返回原结果
相同 Key + 不同指纹 → 拒绝，返回冲突
```

这样可以防止调用方错误地把同一个幂等键用于两种不同订单。

---

## 五、第 2 步：规范化订单项

假设请求中重复出现同一商品：

```json
{
  "items": [
    {"productId": 1, "quantity": 1},
    {"productId": 1, "quantity": 2}
  ]
}
```

系统会先合并成：

```text
商品 1 → 数量 3
```

### 为什么要先合并

- 防止同一订单出现重复商品行；
- 计价更清楚；
- 库存只按最终数量预留；
- 固定商品处理顺序可以降低多商品并发时的死锁概率。

---

## 六、第 3 步：读取权威商品数据

调用：

```text
ProductService.authoritativeSellable(...)
```

这里不会只相信 Redis 展示缓存。

原因：

> 商品页面允许短时间显示旧数据，但最终成交价格和是否可售必须使用数据库中的权威数据。

系统检查：

- 商品是否存在；
- 商品是否已上架；
- 所有商品是否使用同一币种；
- 当前价格是多少。

---

## 七、第 4 步：服务端计算金额

简化计算：

```text
商品小计 = 每项单价 × 数量后累加
最终金额 = 商品小计 - 优惠金额
```

金额使用 `BigDecimal`，并明确保留两位小数和舍入方式。

### 为什么不用 `double`

`double` 是二进制浮点数，部分十进制小数不能被精确表示。金额计算需要可预测的十进制结果，所以使用 `BigDecimal`。

---

## 八、第 5 步：占用优惠券

调用：

```text
CouponService.reserve(...)
```

系统可能检查：

- 优惠券是否存在；
- 是否属于当前用户；
- 是否在有效期内；
- 是否满足最低消费；
- 是否已经使用或被其他订单占用。

优惠券占用必须和订单创建处于同一事务。否则可能出现优惠券显示已占用，但订单没有创建成功。

---

## 九、第 6 步：预留库存

调用：

```text
InventoryService.reserve(...)
```

真正更新在：

```text
InventoryRepository.reserve(...)
```

核心 SQL 类似：

```sql
UPDATE inventory
SET available = available - :qty,
    reserved = reserved + :qty
WHERE product_id = :id
  AND available >= :qty;
```

### 这条 SQL 为什么能防止库存扣成负数

检查库存和扣减库存由数据库在同一条更新中完成。

```text
库存足够 → 更新 1 行
库存不足 → 更新 0 行
```

应用通过“受影响行数”判断是否成功。

这比下面的普通写法安全：

```text
先查询库存
→ Java 中减法
→ 再保存
```

因为两个请求可能同时查到同一个旧库存。

---

## 十、第 7 步：保存订单

系统生成：

- 订单 UUID；
- 便于展示的订单号；
- 用户 ID；
- 小计；
- 优惠金额；
- 最终金额；
- 币种；
- 初始状态；
- 创建时间。

然后通过 `OrderRepository` 保存。

---

## 十一、第 8 步：保存订单项快照

订单项会保存：

- 商品 ID；
- 下单时的商品名称；
- 下单时的 SKU；
- 下单时的成交单价；
- 数量。

### 为什么要保存快照

商品以后可能改名或改价，但历史订单必须保持下单当时的事实。

如果历史订单每次都去读取当前商品价格，用户几个月后查看订单时，金额可能和付款时不一致。

---

## 十二、第 9 步：写入 Outbox

调用：

```text
OutboxService.append(...)
```

它会在数据库中保存一条：

```text
order.created.v1 待发布事件
```

### 为什么不直接在事务中发送 RabbitMQ

数据库事务和 RabbitMQ 不是同一个事务系统。可能出现：

```text
订单提交成功
→ 程序在发消息前宕机
→ 通知消息永久丢失
```

Outbox 做法：

```text
订单数据 + 待发送事件
在同一个数据库事务中一起保存
```

后台发布器稍后反复扫描并发送未发布事件。

---

## 十三、第 10 步：事务提交

到这里没有异常，数据库提交：

```text
幂等记录
优惠券占用
库存预留
订单
订单项快照
Outbox 事件
```

一起正式生效。

任何一步抛出会触发回滚的异常，上述未提交修改一起撤销。

---

## 十四、HTTP 响应返回

Controller 最终返回 `OrderResponse`，Spring 把 Java 对象转成 JSON，HTTP 状态为 201。

示意：

```json
{
  "id": "...",
  "number": "MC-20260903-AB12CD34",
  "status": "PENDING_PAYMENT",
  "subtotal": 200.00,
  "discount": 10.00,
  "total": 190.00,
  "currency": "CNY"
}
```

---

## 十五、事务提交后发生什么

后台 `OutboxPublisher` 定期读取待发布事件：

```text
领取事件
→ 发送到 RabbitMQ
→ 等待 Publisher Confirm
→ 标记为已发布
```

Consumer 收到消息后可能：

- 创建站内通知；
- 记录积分；
- 执行其他异步副作用。

消息可能重复投递，所以 Consumer 需要通过消息 ID 去重，并让去重记录与业务修改在同一事务提交。

---

## 十六、这条链路中每一层的责任

| 层 | 在创建订单中负责什么 |
|---|---|
| Controller | 读取 HTTP 请求、当前用户和幂等键 |
| DTO | 定义允许输入和输出的数据 |
| Application Service | 编排完整下单流程和事务 |
| Domain / Entity | 保护订单状态等业务规则 |
| Repository | 执行数据库查询和更新 |
| PostgreSQL | 保存最终业务事实、约束并发 |
| Redis | 加速允许短暂旧值的读取或做限流等辅助能力 |
| Outbox | 记录待发布事件 |
| RabbitMQ | 异步传递事件 |
| Consumer | 幂等执行通知、积分等副作用 |
| Test | 证明上述规则在正常、失败和并发场景下成立 |

---

## 十七、跟着代码阅读

按下面顺序打开：

```text
OrderController.java
→ OrderDtos.java
→ CreateOrderService.java
→ ProductService.java
→ CouponService.java
→ InventoryService.java
→ InventoryRepository.java
→ OrderEntity.java
→ OrderItemEntity.java
→ OutboxService.java
→ OutboxPublisher.java
→ OrderPaidConsumers.java
```

每打开一个文件，只回答：

```text
它接收什么？
它做什么？
它把结果交给谁？
```

## 十八、读完后的自测

关闭本文后讲清楚：

1. 为什么请求中不能提交最终价格？
2. 为什么创建订单需要幂等键和请求指纹？
3. 为什么 `@Transactional` 不能单独解决超卖？
4. 库存条件 UPDATE 怎样工作？
5. 为什么订单项保存商品快照？
6. Outbox 解决什么问题？
7. 为什么使用 Outbox 后 Consumer 仍然要幂等？
