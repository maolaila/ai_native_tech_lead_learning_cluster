# ADHD 友好的项目学习计划

这份计划的目标不是让你一天学很多，而是让你**持续学、少跑题、每次都有明确产出**。

它不替代医疗建议，只解决本项目的学习组织问题。

---

## 一、总规则：一次只解决一个问题

每个学习单元开始前，先写一句：

```text
这 20 分钟，我只想弄懂：____________________
```

合格的问题：

- 创建订单请求从哪里进入？
- `@Transactional` 为什么放在 `create()` 上？
- 库存为 1 时怎样防止 20 个请求都成功？
- Outbox 为什么还需要消费者幂等？

不合格的问题：

- 今天把 Spring 学完；
- 今天搞懂数据库；
- 今天看完整个工程；
- 今天研究所有注解。

问题越小，越容易完成。

---

## 二、一次最多打开 5 个文件

推荐限制：

```text
1 个入口文件
+ 1 个业务文件
+ 1 个数据文件
+ 1 个测试文件
+ 1 个对应文档
```

超过 5 个文件时，把新发现的文件记到“稍后清单”，不要马上打开。

### 稍后清单模板

```text
当前问题：库存怎样防超卖？

稍后再看：
- PostgreSQL MVCC 细节
- 乐观锁与悲观锁性能差异
- Hibernate 一级缓存
```

记下来后继续当前问题。记录不等于现在必须解决。

---

## 三、使用 20 + 5，而不是硬撑两小时

一个学习循环：

```text
20 分钟专注
→ 5 分钟离开屏幕
→ 20 分钟复述或实验
→ 结束或再开下一轮
```

第一轮用于输入：看代码和文档。

第二轮用于输出：画图、写三句话、运行测试或修改一处代码。

只看不输出，很容易产生“好像懂了”的错觉。

---

## 四、每次学习必须有一个可见结果

可见结果只能选一个：

- 一张调用链图；
- 三句话总结；
- 一条测试；
- 一次接口调用结果；
- 一段自己写的注释；
- 一个 Bug 复现；
- 一段 3 分钟口头讲解录音。

不要把“看了 30 页”当成结果。

---

## 五、陌生词处理顺序

遇到陌生词时，不要直接打开搜索引擎。

固定顺序：

```text
1. 看代码上方中文注释
2. 查 SPRING-JAVA-ANNOTATIONS.md
3. 查 BACKEND-TERMS-PLAIN-CHINESE.md
4. 查 JAVA-SYNTAX-FOR-BACKEND-BEGINNERS.md
5. 查代码注释中的“对应文档”
6. 仍然不懂，才允许外部搜索
```

外部搜索时也只搜索一个问题，并设置 10 分钟计时器。

### 防跑题搜索句式

不要搜索：

```text
Spring Boot 原理
```

改成：

```text
Spring Boot @Transactional 同类内部调用为什么不生效
```

问题越具体，越不容易跑远。

---

## 六、阅读代码时使用三色标记

不需要真的使用三种颜色，也可以用三个符号。

```text
✓ 已懂：能用自己的话讲
? 暂时不懂：和当前问题有关，必须解决
→ 稍后：和当前问题无关，先放到稍后清单
```

只处理 `?`，不要被 `→` 带走。

---

## 七、每个文件只做三件事

打开一个 Java 文件后，只找：

1. 这个类的输入是什么？
2. 它做了什么关键动作？
3. 它把结果交给谁？

例如 `OrderController`：

```text
输入：HTTP Header + JSON 请求体
关键动作：取得当前用户并调用创建订单服务
输出：OrderResponse
```

第一遍不要逐个研究每个 import。

---

## 八、每天的学习模板

复制下面内容到自己的笔记：

```text
日期：
今天只解决的问题：

本次最多打开的文件：
1.
2.
3.
4.
5.

我现在的猜测：

20 分钟后，我确认了：
1.
2.
3.

仍然不懂但必须解决：

稍后再看的内容：

我能否在 3 分钟内讲清楚：能 / 不能
下一次从哪里继续：
```

最后一行非常重要。下次开始时不用重新寻找入口。

---

## 九、12 个学习阶段

不要按“读完多少页”推进。每个阶段都要完成一个业务闭环。

## 阶段 1：看懂 HTTP 请求怎样进入后端

阅读：

- `OrderController.java`
- `OrderDtos.java`
- `02_backend_spring/01_请求生命周期与IoC_DI.md`
- `02_backend_spring/04_API设计_校验_异常与错误码.md`

输出：画出 `POST /api/orders` 进入 Controller 的流程。

---

## 阶段 2：看懂 Controller、Service、Repository

阅读：

- `ProductController.java`
- `ProductService.java`
- `ProductRepository.java`
- `02_backend_spring/02_Controller_Service_Repository分层.md`

输出：用“接待、业务负责人、数据库窗口”三个比喻讲清分层。

---

## 阶段 3：看懂 Entity、DTO 和数据库表

阅读：

- `CartItemEntity.java`
- `OrderDtos.java`
- Flyway 的建表脚本
- `02_backend_spring/03_DTO_Entity_Domain与映射.md`

输出：解释为什么不能直接把 Entity 当作 API 响应。

---

## 阶段 4：看懂事务

阅读：

- `CreateOrderService.create()`
- `04_database_postgresql/04_事务与Spring边界.md`

实验：在一个测试中故意让保存订单后抛异常，观察数据库是否回滚。

输出：说清哪些操作必须一起成功或一起失败。

---

## 阶段 5：看懂库存并发

阅读：

- `InventoryService.java`
- `InventoryRepository.java`
- `InventoryConcurrencyIT.java`
- `04_database_postgresql/05_并发_锁与库存超卖.md`

输出：用库存为 1、20 个请求同时购买的例子解释原子更新。

---

## 阶段 6：看懂认证和权限

阅读：

- `AuthController.java`
- `AuthService.java`
- `JwtAuthenticationFilter.java`
- `SecurityConfiguration.java`
- `05_auth_security/`

输出：区分认证、角色权限和对象级权限。

---

## 阶段 7：看懂 Redis

阅读：

- `ProductCacheService.java`
- `RateLimitService.java`
- `RedisLockService.java`
- `06_redis/`

实验：停止 Redis，观察哪些读取可以降级，哪些关键业务仍以数据库为准。

输出：说明缓存为什么不能决定订单成交价。

---

## 阶段 8：看懂 RabbitMQ 和 Outbox

阅读：

- `OutboxService.java`
- `OutboxPublisher.java`
- `RabbitTopology.java`
- `ProcessedMessageService.java`
- `07_rabbitmq/`

输出：画出“数据库事务 → Outbox → RabbitMQ → Consumer”的流程。

---

## 阶段 9：看懂支付和回调

阅读：

- `PaymentOrchestrator.java`
- `PaymentTransactionService.java`
- `PaymentWebhookService.java`
- `WebhookSignature.java`

实验：模拟超时、重复回调和错误签名。

输出：解释“请求超时为什么不一定代表支付失败”。

---

## 阶段 10：看懂测试体系

阅读顺序：

```text
MoneyTest
→ OrderEntityTest
→ WebhookSignatureTest
→ CreateOrderIT
→ InventoryConcurrencyIT
→ ArchitectureTest
```

输出：为每条测试标注它提供的是行为、数据、并发、故障还是架构证据。

---

## 阶段 11：看懂运行和排错

阅读：

- `application.yml`
- `compose.yaml`
- Dockerfile
- Prometheus、Grafana、Tempo 配置
- `10_observability/`

输出：从一个 `traceId` 找到接口日志、数据库操作和异步消费者结果。

---

## 阶段 12：看懂 MCP 和 AI 工程治理

阅读：

- `mcp-server/`
- `ai-engineering/`
- `13_ai_engineering_mcp/`

输出：解释为什么 MCP Tool 不应该提供“任意执行 Shell”或“任意写生产数据库”。

---

## 十、卡住超过 15 分钟怎么办

按下面顺序：

1. 把问题缩小一半；
2. 找同目录测试；
3. 找代码上方“对应文档”；
4. 运行代码或加断点；
5. 写出自己当前的错误猜测；
6. 再查资料。

例子：

原问题太大：

```text
为什么事务会失效？
```

缩小为：

```text
为什么 CreateOrderService.create() 由 Controller 调用时事务生效？
```

再缩小为：

```text
@Transactional 是谁读取的？调用是否经过 Spring 管理的对象？
```

---

## 十一、停止规则

满足任意一项就停止当前学习单元：

- 已经完成预定输出；
- 连续 5 分钟只是滚动页面，没有新增理解；
- 打开的文件超过 5 个；
- 开始研究和当前问题无关的底层细节；
- 明显疲劳，开始反复读同一行。

停止不是失败。停止并记录“下一步从哪里继续”，能降低下次启动成本。

---

## 十二、每周复盘只回答五个问题

```text
1. 这周我能不看源码讲清哪一条业务链？
2. 哪个知识点我只是认识名字，还不会解释？
3. 我运行了哪个测试或故障实验？
4. 我被哪些无关资料带跑了？
5. 下周只解决哪三个问题？
```

不要写很长的复盘。每题 1～3 句话即可。

## 十三、判断是否可以进入下一阶段

同时满足：

- 能画流程；
- 能说出至少三个关键规则；
- 能指出一个失败场景；
- 能找到对应测试；
- 能用通俗语言讲 3 分钟。

否则继续当前阶段，不要因为“计划表到期”强行跳过。
