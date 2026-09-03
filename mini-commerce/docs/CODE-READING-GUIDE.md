# Mini Commerce 源码阅读指南

这份工程不是按文档章节拆成互不相关的示例，而是用一条真实电商业务链把后端、数据库、Redis、RabbitMQ、安全、测试、运行和 AI 工程串起来。

> 阅读原则：先沿业务调用链理解“发生了什么”，再回到技术专题理解“为什么这样做”。不要从所有 Entity 或配置文件逐个背诵。

## 1. 先认识代码中的三类学习注释

主源码文件应包含以下内容：

```java
/**
 * 作用：这个类在业务链路中的职责。
 * 为什么：为什么放在这一层、为什么不用更简单但有风险的写法。
 * 对应文档：可以回到学习集群继续阅读的文件路径。
 */
```

高风险方法还会额外解释：

- 事务为什么从这里开始；
- 并发为什么不能只靠 `@Transactional`；
- 幂等为什么需要请求指纹和数据库唯一约束；
- Outbox 为什么仍然要求消费者幂等；
- 缓存为什么不能作为订单价格和库存的最终事实源；
- 支付、退款和回调为什么不能当作普通 CRUD。

Getter、简单构造器和一眼可知的转发代码不会堆积无意义注释。

## 2. 第一遍：只读一条完整下单链路

按下面顺序阅读：

1. `backend/src/main/java/com/example/minicommerce/order/api/OrderController.java`
   - 看 HTTP 请求怎样进入系统；
   - 看认证用户和 `Idempotency-Key` 怎样传给应用服务；
   - Controller 不直接操作 Repository。
2. `backend/src/main/java/com/example/minicommerce/order/api/OrderDtos.java`
   - 看客户端允许提交哪些字段；
   - 注意客户端不能提交最终成交金额。
3. `backend/src/main/java/com/example/minicommerce/order/application/CreateOrderService.java`
   - 这是下单用例的事务边界和主阅读入口；
   - 按方法内顺序画一张时序图。
4. `backend/src/main/java/com/example/minicommerce/catalog/application/ProductService.java`
   - 看下单为什么绕过展示缓存，重新读取权威商品数据。
5. `backend/src/main/java/com/example/minicommerce/inventory/application/InventoryService.java`
   - 看库存预留、恢复和确认成交的区别。
6. `backend/src/main/java/com/example/minicommerce/inventory/infrastructure/InventoryRepository.java`
   - 找到条件原子 `UPDATE`；
   - 用“库存为 1、20 个请求并发”解释为什么它不会超卖。
7. `backend/src/main/java/com/example/minicommerce/promotion/application/CouponService.java`
   - 看最低金额、有效期、归属和重复使用怎样被保护。
8. `backend/src/main/java/com/example/minicommerce/order/infrastructure/OrderEntity.java`
   - 看订单状态机；
   - 找出为什么不允许任意 `setStatus`。
9. `backend/src/main/java/com/example/minicommerce/order/infrastructure/OrderItemEntity.java`
   - 看商品名称、SKU 和成交价格快照。
10. `backend/src/main/java/com/example/minicommerce/messaging/application/OutboxService.java`
    - 看订单与待发布事件为什么同事务写入。

读完后，应该可以不看源码画出：

```text
HTTP 请求
→ 参数和权限
→ 幂等锁/请求指纹
→ 权威商品读取
→ 服务端计价
→ 优惠券占用
→ 库存预留
→ 订单与快照
→ Outbox
→ 提交事务
```

## 3. 第二遍：追踪异步事件

按顺序阅读：

1. `messaging/application/OutboxPublisher.java`
2. `messaging/infrastructure/OutboxJdbcRepository.java`
3. `messaging/config/RabbitTopology.java`
4. `messaging/application/EventEnvelope.java`
5. `messaging/application/ProcessedMessageService.java`
6. `notification/` 下的消费者与通知记录

必须能回答：

- 数据库提交后、消息发送前宕机怎么办？
- Broker 收到消息但 Confirm 丢失怎么办？
- Consumer 完成数据库提交、Ack 前宕机怎么办？
- 为什么“消息至少投递一次”不等于“业务副作用执行多次”？
- 为什么去重记录和业务副作用必须在同一事务中？

对应文档：

- `07_rabbitmq/03_Confirm_Ack_Retry_DLQ.md`
- `07_rabbitmq/04_幂等与Outbox.md`
- `07_rabbitmq/05_消息契约_顺序与积压.md`

## 4. 第三遍：阅读 Redis，但始终记住数据库是权威源

优先寻找以下实现：

- 商品 Cache Aside；
- Null Cache；
- TTL 抖动；
- Single Flight；
- 主动失效；
- Lua 限流；
- Redis 故障时的受控回源。

阅读时做两个对照实验：

```text
场景 A：缓存价格 800，数据库价格 1000
预期：商品页可能短暂显示旧值，但下单成交价必须是数据库权威价格。

场景 B：Redis 停机
预期：允许降级的读取可回源；回源并发必须受控，不能把数据库打垮。
```

对应文档：`06_redis/`。

## 5. 第四遍：认证、授权和支付

### 认证与权限

阅读：

- `identity/`；
- `shared/security/` 或安全配置；
- 订单查询中的对象级权限判断。

区分：

```text
Authentication：请求者是谁
RBAC：该角色拥有什么能力
Object Authorization：这个具体订单是否属于请求者
```

前端隐藏按钮不是安全控制，必须从后端 API 测试他人订单访问。

### 支付

阅读支付意图、外部调用、Webhook 验签、重复事件和退款代码。重点观察外部调用为什么不放在持有数据库锁的长事务里。

对应文档：

- `05_auth_security/`
- `11_system_design/04_韧性_Timeout_Retry_Circuit.md`

## 6. 第五遍：用测试反向理解代码

测试阅读顺序：

1. 纯领域和金额规则 Unit Test；
2. Repository/事务 Integration Test；
3. API 认证、校验和错误结构 Test；
4. 库存并发 Test；
5. Outbox/Consumer 幂等 Test；
6. Architecture Test；
7. E2E Smoke。

每看一个测试，都写下它提供哪种证据：

```text
行为证据
数据证据
自动化证据
故障证据
```

不要把“覆盖率高”当成“业务一定正确”。

## 7. 第六遍：运行、发布和可观测性

阅读顺序：

1. `backend/src/main/resources/application.yml`
2. `infra/compose.yaml`
3. Dockerfile
4. Prometheus/Grafana/Tempo/OpenTelemetry 配置
5. `.github/workflows/`
6. Migration、Smoke 和 Rollback 脚本

把一次请求关联到：

```text
requestId / traceId
→ API 日志
→ 数据库操作
→ Outbox eventId
→ RabbitMQ Consumer
→ 通知或积分结果
```

## 8. 格式化和注释质量门禁

本项目不再依赖开发者手工格式化：

```bash
cd mini-commerce/backend
mvn spotless:apply   # 自动格式化
mvn spotless:check   # 检查是否有未格式化代码
```

仓库还提供：

```bash
python tools/check_learning_readability.py
```

该检查会阻止：

- 一个完整类被压缩成几行；
- 主源码没有中文职责说明；
- 主源码没有对应文档路径；
- 关键事务/并发方法缺少原因解释；
- Tab 和行尾空格重新进入仓库。

审计结果生成到：

```text
docs/generated/readability-audit.md
```

## 9. 每个模块的学习输出

阅读一个模块后，不要只说“看懂了”，至少输出：

1. 一张模块边界图；
2. 一张主流程时序图；
3. 三条业务不变量；
4. 三个失败场景；
5. 对应自动化测试；
6. 一个你认为可以改进的设计及其代价；
7. 一次不看文档的口头讲解。

能完成这些输出，才说明代码已经从“看过”变成了自己的工程能力。
