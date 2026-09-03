# Mini Commerce 完整学习工程

这不是按章节拆开的 Hello World 集合，而是一套可运行的模块化单体。所有知识点都落在同一个电商业务：用户浏览商品、加入购物车、使用优惠券创建订单、预留库存、模拟支付、处理重复回调、异步通知和积分，并具备测试、发布、监控、云映射和 AI 工程治理。

## 后端小白先从这里开始

不要一上来从 Entity、配置类或所有目录逐个硬啃。先按下面顺序阅读：

1. [`docs/BEGINNER-START-HERE.md`](docs/BEGINNER-START-HERE.md)：后端零基础入口，只先建立请求、业务和数据库的主框架；
2. [`docs/REQUEST-TO-DATABASE-WALKTHROUGH.md`](docs/REQUEST-TO-DATABASE-WALKTHROUGH.md)：跟着一条创建订单请求，从 HTTP 一直走到数据库和 RabbitMQ；
3. [`docs/SPRING-JAVA-ANNOTATIONS.md`](docs/SPRING-JAVA-ANNOTATIONS.md)：`@Value`、`@Service`、`@Transactional`、`@Entity` 等注解的通俗解释；
4. [`docs/BACKEND-TERMS-PLAIN-CHINESE.md`](docs/BACKEND-TERMS-PLAIN-CHINESE.md)：事务、幂等、缓存、Outbox、Ack 等专有名词的通俗词典；
5. [`docs/JAVA-SYNTAX-FOR-BACKEND-BEGINNERS.md`](docs/JAVA-SYNTAX-FOR-BACKEND-BEGINNERS.md)：阅读本项目所需的 Java 语法速查；
6. [`docs/CONFIGURATION-FROM-ZERO.md`](docs/CONFIGURATION-FROM-ZERO.md)：配置文件、环境变量、Profile、`@Value` 和 `@ConfigurationProperties`；
7. [`docs/ADHD-FOCUSED-LEARNING-PLAN.md`](docs/ADHD-FOCUSED-LEARNING-PLAN.md)：一次只解决一个问题、最多打开 5 个文件的学习方法；
8. [`docs/BEGINNER-FAQ.md`](docs/BEGINNER-FAQ.md)：阅读中最常见的后端问题。

遇到陌生词时，固定按这个顺序处理：

```text
代码旁中文注释
→ 注解词典
→ 通俗术语词典
→ Java 语法速查
→ 对应文档章节
→ 前面都没有，再查外部资料
```

这样可以尽量避免从一个词跳到很多网页，最后忘记原来在看哪段代码。

## 源码阅读主线

已经具备基础后，再阅读：

1. [`docs/CODE-READING-GUIDE.md`](docs/CODE-READING-GUIDE.md)：完整的六遍源码阅读路线；
2. [`docs/generated/readability-audit.md`](docs/generated/readability-audit.md)：格式化、中文职责说明和文档映射的自动检查结果；
3. [`docs/generated/document-code-map.md`](docs/generated/document-code-map.md)：文档章节与工程文件的双向映射；
4. [`docs/generated/annotation-usage-index.md`](docs/generated/annotation-usage-index.md)：每种注解在真实源码中的使用位置；
5. `api/mini-commerce.http`：用真实 HTTP 请求走通登录、商品、购物车、下单、支付和通知；
6. `backend/src/test/java/`：从测试反向确认业务规则、事务、并发和架构边界。

主 Java 文件中的学习注释分三类：

```text
作用：这个类或方法在业务流程中负责什么
为什么：为什么采用这种实现，以及它避免了什么错误
对应文档：可以回到学习集群继续阅读的章节路径
```

普通 getter 和显然的字段赋值不会堆积无意义注释；事务、库存并发、幂等、缓存、消息、安全和支付等高风险路径会解释“为什么”。代表性注解还会在代码附近给出通俗说明。

## 技术基线

- Java 21、Spring Boot 3.5.7、Maven；
- PostgreSQL + Flyway；
- Redis：Cache Aside、Null Cache、TTL 抖动、Single Flight、Lua 限流、短期锁；
- RabbitMQ：Topic Exchange、Confirm、Retry、DLQ；
- Transactional Outbox + 幂等 Consumer；
- JWT Access/Refresh、RBAC、对象级权限、HMAC Webhook；
- Actuator、Micrometer、Prometheus、Grafana、OpenTelemetry、Tempo；
- Docker Compose、Kubernetes、AWS Terraform；
- Python MCP SDK 2.1.1、只读工具、沙箱、审计和 Eval。

## 目录

```text
backend/          Spring Boot 模块化单体、Flyway、Unit/Integration/Architecture Test
mcp-server/       MCP Server 2.x：知识检索、Schema、只读 Explain、受控测试
ai-engineering/   Rules、Golden Paths、Eval 数据集
infra/            Compose 配套、Prometheus/Grafana/Tempo、K8s、AWS Terraform
labs/             百万订单、EXPLAIN、死锁、负载实验
api/              可直接执行的 HTTP 请求集
scripts/          Smoke、备份与恢复验证
docs/             小白入口、词典、架构、领域、安全、部署、可观测性和文档映射
```

## 最值得先读的业务代码

1. `backend/src/main/java/com/example/minicommerce/order/api/OrderController.java`：HTTP 请求怎样进入系统；
2. `backend/src/main/java/com/example/minicommerce/order/application/CreateOrderService.java`：完整下单事务；
3. `backend/src/main/java/com/example/minicommerce/inventory/infrastructure/InventoryRepository.java`：条件原子更新防超卖；
4. `backend/src/main/java/com/example/minicommerce/order/infrastructure/OrderEntity.java`：订单状态机；
5. `backend/src/main/java/com/example/minicommerce/payment/application/PaymentOrchestrator.java`：外部调用为什么不放进长事务；
6. `backend/src/main/java/com/example/minicommerce/messaging/application/OutboxPublisher.java`：领取、Confirm、失败重试；
7. `backend/src/main/java/com/example/minicommerce/notification/application/OrderPaidConsumers.java`：事务内消息去重与副作用；
8. `backend/src/main/java/com/example/minicommerce/catalog/application/ProductCacheService.java`：缓存穿透、击穿和雪崩保护；
9. `backend/src/main/java/com/example/minicommerce/shared/security/`：认证和授权边界；
10. `mcp-server/src/mini_commerce_mcp/`：受控 AI 工具。

## 本地运行

```bash
cp .env.example .env
docker compose --profile app up -d --build
./scripts/smoke.sh
```

默认账号仅由 `local` Profile 创建：

- `alice@example.com / Password123!`
- `admin@example.com / AdminPassword123!`

管理界面不是重点。使用 `api/mini-commerce.http`、curl 或任意 API Client 操作。

## 格式化和可读性门禁

```bash
cd backend
mvn spotless:apply   # 自动格式化 Java
mvn spotless:check   # 检查是否有未格式化源码
cd ../..
python3 tools/check_learning_readability.py
python3 tools/check_beginner_learning_assets.py
```

Spotless 已绑定到 Maven `validate` 阶段，因此未格式化代码会在正常构建早期失败。可读性检查还会阻止主源码缺少中文职责说明、缺少对应文档和关键原因解释。初学者资料检查会验证小白入口、注解词典、术语词典、配置说明和代码内代表性注解说明是否仍然存在。

## 测试

```bash
cd backend && mvn -B verify
cd ../mcp-server && python -m pip install -e '.[dev]' && pytest -q
cd .. && python3 ai-engineering/eval/run_static_eval.py
python3 tools/check_learning_references.py
```

Testcontainers 在存在 Docker 的环境执行真实 PostgreSQL Migration、事务和库存并发测试；没有 Docker 时相关测试会明确跳过，不能把跳过宣称为通过。

## 关键设计选择

- PostgreSQL 是订单、库存、金额、支付和权限的权威事实源；Redis 不能替代它。
- 创建订单不接收客户端最终价格。
- 订单项保存历史成交快照。
- 订单创建使用数据库事务级 advisory lock + 唯一约束实现 API 幂等。
- 库存使用条件 UPDATE；不使用 JVM `synchronized` 作为多实例正确性方案。
- 外部支付调用位于数据库事务外，结果通过短事务落库。
- Outbox 解决数据库与消息双写；消费者仍需幂等。
- MCP 默认只读，不提供任意 Shell、生产写 SQL、Secret 读取或无审批部署。

完整章节映射见 `docs/generated/document-code-map.md`。
