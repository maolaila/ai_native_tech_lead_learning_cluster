# 后端零基础：从这里开始

这份说明把你当成**第一次系统学习后端的人**。你不需要先去网上补一大堆课，也不用一次弄懂所有名词。

本仓库的学习目标不是让你背注解，而是让你逐步看懂下面这条真实业务链：

```text
用户发请求
→ Controller 接住请求
→ Service 执行业务规则
→ Repository 读写数据库
→ Redis 加速部分读取
→ RabbitMQ 处理异步任务
→ 测试证明规则没有被破坏
→ 日志、指标和链路帮助排错
```

## 一、先记住四句话

1. **Controller 是门口接待。** 它接收 HTTP 请求，检查请求格式，然后把任务交给业务层。
2. **Service 是业务负责人。** 它决定一件业务应该按什么顺序完成。
3. **Repository 是数据库窗口。** 它负责查询和保存数据，不负责决定业务规则。
4. **数据库是重要业务事实的最终依据。** Redis 可以加速，但订单金额、库存和支付状态不能只相信缓存。

只要先记住这四句话，你就有了阅读本项目的主框架。

## 二、第一次打开项目，不要从 Entity 开始

初学者很容易打开 `Entity`，看到十几个注解就卡住。正确顺序是从一次真实请求开始。

先读下面 5 个文件：

1. `backend/src/main/java/com/example/minicommerce/order/api/OrderController.java`
2. `backend/src/main/java/com/example/minicommerce/order/api/OrderDtos.java`
3. `backend/src/main/java/com/example/minicommerce/order/application/CreateOrderService.java`
4. `backend/src/main/java/com/example/minicommerce/inventory/application/InventoryService.java`
5. `backend/src/main/java/com/example/minicommerce/inventory/infrastructure/InventoryRepository.java`

每个文件只回答一个问题：

| 文件 | 只回答这个问题 |
|---|---|
| `OrderController` | 请求从哪里进入系统？ |
| `OrderDtos` | 前端允许提交哪些数据？ |
| `CreateOrderService` | 创建订单要按什么顺序做？ |
| `InventoryService` | 库存预留、恢复和成交有什么区别？ |
| `InventoryRepository` | 数据库怎样防止库存被扣成负数？ |

不要在第一遍追求每行都懂。先弄懂“谁调用谁”。

## 三、一次请求到底发生了什么

以“创建订单”为例：

```text
POST /api/orders
        │
        ▼
OrderController
接收请求体和 Idempotency-Key
        │
        ▼
CreateOrderService
校验商品、服务端计价、占用优惠券、预留库存
        │
        ├── ProductService：读取可售商品
        ├── CouponService：检查优惠券
        ├── InventoryService：预留库存
        ├── OrderRepository：保存订单
        ├── OrderItemRepository：保存成交快照
        └── OutboxService：保存待发送事件
        │
        ▼
数据库事务提交
以上操作一起成功，或者一起撤销
```

这里最重要的不是类名，而是这条规则：

> 创建订单涉及的关键数据库修改必须“同成同败”。库存扣了但订单没保存，或者订单保存了但库存没扣，都会产生错误数据。

这就是 `@Transactional` 在该方法上的主要作用。

## 四、你会经常看到的目录

```text
api/             HTTP 请求入口、请求参数、响应结构
application/     一个完整业务用例的执行顺序
 domain/         业务状态、业务动作和不能被破坏的规则
infrastructure/  数据库、Redis、RabbitMQ、外部服务等技术实现
config/          Spring、消息队列和安全等集中配置
test/            自动验证业务规则
```

### `api`

大白话：系统对外开的窗口。

这里常见：

- `Controller`：接收请求；
- `DTO`：请求和响应的数据盒子；
- 参数校验：例如名称不能为空、数量必须大于 0。

### `application`

大白话：业务流程编排处。

例如创建订单要依次做：

```text
校验请求 → 查商品 → 算价格 → 占优惠券 → 预留库存 → 保存订单
```

### `domain`

大白话：真正的业务规则。

例如订单不能从 `CANCELLED` 直接变成 `PAID`，这种规则应由领域对象保护，而不是让任何代码随便 `setStatus()`。

### `infrastructure`

大白话：和具体技术打交道的地方。

例如：

- JPA 怎样映射数据库表；
- SQL 怎样更新库存；
- Redis 怎样读写缓存；
- RabbitMQ 怎样发送消息。

## 五、Java 代码暂时只需要掌握这些

第一阶段只需要认识：

- `class`：定义一种对象；
- `interface`：规定“需要提供哪些能力”，不一定写具体做法；
- `record`：主要用来装数据的简洁类型；
- 构造器：创建对象时传入必要依赖；
- 方法：一段可以被调用的行为；
- `if`：条件判断；
- `for`：重复处理多项数据；
- `try/catch`：处理可能失败的操作；
- `Optional`：明确表示“可能有值，也可能没有值”；
- `List`、`Map`、`Set`：常见集合；
- `BigDecimal`：处理金额，避免浮点误差；
- `UUID`：一种很难重复的 ID。

完整说明见：[Java 后端阅读语法速查](JAVA-SYNTAX-FOR-BACKEND-BEGINNERS.md)。

## 六、看到注解时怎么处理

注解通常以 `@` 开头，例如：

```java
@Service
@Transactional
@Entity
@GetMapping
```

先把注解理解成一张贴在代码上的“说明标签”。Spring 或 JPA 看到标签后，会做额外工作。

例如：

```java
@Service
public class CreateOrderService {
}
```

大白话：

> `@Service` 告诉 Spring：“这个类负责业务操作，请在程序启动时创建并管理它。”

再例如：

```java
@Transactional
public OrderResponse create(...) {
}
```

大白话：

> `@Transactional` 告诉 Spring：“这个方法里的数据库修改要作为一个整体提交；中途出错时要一起回滚。”

完整说明见：[Spring 与 Java 注解小白词典](SPRING-JAVA-ANNOTATIONS.md)。

## 七、碰到陌生词，不要立刻离开项目搜索

按下面顺序处理：

```text
1. 看代码上方的中文注释
2. 看 SPRING-JAVA-ANNOTATIONS.md
3. 看 BACKEND-TERMS-PLAIN-CHINESE.md
4. 看对应的文档章节
5. 前四步都没有解释，再查外部资料
```

这样做是为了避免从一个陌生词跳到十几个网页，最后忘了原本在看哪段代码。

## 八、第一天只做这些

### 第 1 个 20 分钟

阅读：

- 本文件；
- `OrderController.java`；
- `OrderDtos.java`。

输出三句话：

1. 创建订单接口的地址是什么？
2. 请求需要哪些字段？
3. 为什么不能让前端直接提交最终价格？

### 第 2 个 20 分钟

阅读 `CreateOrderService.create()`，只标出这些步骤：

```text
幂等 → 商品 → 价格 → 优惠券 → 库存 → 订单 → Outbox
```

暂时不要研究每个类的内部实现。

### 第 3 个 20 分钟

阅读：

- `InventoryService.reserve()`；
- `InventoryRepository.reserve()`。

用自己的话回答：

> 库存为 1 时，为什么 20 个并发请求不会全部成功？

## 九、初学者阶段允许“不懂”

第一遍可以暂时跳过：

- AOP 的底层代理实现；
- Hibernate 内部状态机；
- PostgreSQL 查询优化器源码；
- RabbitMQ 协议帧；
- JVM 字节码细节；
- OpenTelemetry Collector 内部实现；
- MCP 协议的全部扩展能力。

这些不是没用，而是现在不是最先需要解决的问题。

第一阶段只要求你能说清楚：

```text
请求从哪里进来
→ 业务在哪执行
→ 数据保存在哪里
→ 失败时怎样回滚
→ 重复请求怎样避免重复下单
→ 并发时怎样防止超卖
```

## 十、判断自己是否真的看懂

不要用“我好像看懂了”判断。关闭源码后，完成下面四件事：

1. 画出创建订单的调用链；
2. 说出三个不能被破坏的业务规则；
3. 说出两个可能失败的位置；
4. 指出哪个测试可以证明对应规则。

能够不看答案讲出来，才算真正掌握。

下一步阅读：[ADHD 友好的学习计划](ADHD-FOCUSED-LEARNING-PLAN.md)。
