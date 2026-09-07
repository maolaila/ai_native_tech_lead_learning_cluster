# 正式学习说明：先跑通，再按一条业务链阅读

本页是当前学习版本的统一入口。它不是“绝对没有 Bug”的保证，也不是生产系统认证。质量判断同时依赖源码审查、可重复测试和当前提交的 CI，不能只看文件数量或绿色的格式检查。

## 1. 你现在要用哪一部分

**第一阶段只用本地后端闭环。** 不必先准备 AWS、Kubernetes、Node、前端页面或真实支付账号。

| 内容 | 当前定位 |
|---|---|
| Java 21 / Spring Boot 3.5.7 / Maven | 可执行后端参考实现；版本以 pom.xml 为准 |
| PostgreSQL 17、Redis 8、RabbitMQ 4 | Compose 中的真实依赖，不是内存替代品 |
| 创建订单、幂等、库存预留、模拟支付、取消、通知、积分 | 当前主学习链；从 HTTP 到数据库再到消息 |
| 退款 | 付款后、履约前的全额模拟退款；不包含部分退款、退货入库和积分冲正 |
| MCP | 实际协议服务与只读知识工具；有边界测试，不是完整操作系统沙箱 |
| Prometheus/Grafana/Collector/Tempo | 本地可观测性配置；跨消息的完整 Span 传播仍需扩展 |
| Kubernetes / AWS Terraform | 部署参考模板与静态校验；未替你创建云资源或验证真实生产网络 |
| 前端、Playwright、SLO、故障实验、AI 对照实验 | 学习任务或材料，不表示仓库已交付所有成品和实验结论 |

根目录的阶段门和验收清单是**你需要逐步完成的目标**。文档—代码映射是定位辅助，不表示一个相关文件已经实现该章所有要求。

## 2. 最少环境与启动

需要 Docker Engine/Desktop 正常运行，Docker Compose 支持 `--wait`，Python 3.12 或 3.13 可用。仅通过容器运行后端时，本机不必安装 Java；阅读、修改和运行 Java 测试时再准备 Java 21、Maven 3.9.x。Windows 下以下命令放在 WSL2 执行；`python3` 在 Windows 原生终端可能对应 `py -3`。

从仓库根目录开始：

```bash
cd mini-commerce
test -f .env || cp .env.example .env
# 第一次拉镜像和编译需要联网；--wait 等待健康检查，不把“容器已创建”当成可用。
docker compose --profile app up -d --build --wait --wait-timeout 180
python3 scripts/smoke.py
```

Smoke 会创建带随机后缀的测试账户和商品，验证注册、登录、下单、同键重试、模拟支付、查询落库状态、异步通知和退款。它会留下演示数据；**只用于 local 学习环境，不能指向生产**。默认密码不是机密配置，更不是上线凭证。

运行失败时先看：

```bash
docker compose ps
docker compose logs --tail=100 backend
```

`Connection refused` 先检查依赖服务和端口；`Flyway` 或 `Schema-validation` 先看数据库迁移；不要为了让启动变绿，把 `ddl-auto=validate` 改成 `update` 或关闭 Flyway。

可选监控：

```bash
docker compose --profile app --profile observability up -d --build --wait --wait-timeout 180
```

停止但保留演示数据：

```bash
docker compose --profile app --profile observability down
```

不要习惯性加 `-v`：它会删除这个 Compose 项目的数据卷。

## 3. 主机地址和容器地址不是一回事

下面是默认值；更改 `.env` 后以实际配置为准。所有映射端口绑定 `127.0.0.1`，不供局域网直接访问。

| 服务 | 你在宿主机使用 | Compose 容器互相访问 |
|---|---|---|
| 后端 | `http://127.0.0.1:18080` | `backend:8080` |
| PostgreSQL | `localhost:15432`，库名 `commerce` | `postgres:5432` |
| Redis | `localhost:16379` | `redis:6379` |
| RabbitMQ AMQP 协议 | `localhost:15672`，不是网页 | `rabbitmq:5672` |
| RabbitMQ 管理网页 | `http://127.0.0.1:15673` | `rabbitmq:15672` |
| MCP | `http://127.0.0.1:18081/mcp` | `mcp-server:8081/mcp` |
| Prometheus | `http://127.0.0.1:19090` | `prometheus:9090` |
| Grafana | `http://127.0.0.1:13000` | `grafana:3000` |

只启动依赖、从源码运行后端的另一种方式（不要同时启动占用相同端口的两个后端）：

```bash
# 当前目录 mini-commerce
docker compose up -d --wait postgres redis rabbitmq
cd backend
mvn spring-boot:run -Dspring-boot.run.profiles=local
```

此模式后端默认是 **8080**，不是 18080。另开终端运行 Smoke 时设置 `BASE_URL=http://127.0.0.1:8080`。只启动 app、不启动 observability 时，未配置的 OTLP 接收端可能有连接警告，不表示订单数据库事务失败。

## 4. 演示数据与返回字段

只在 `local` Profile 初始化：Alice 的账号是 `alice@example.com / Password123!`；管理员是 `admin@example.com / AdminPassword123!`。新库里机械键盘单价 `8000.00 JPY`、库存 100；无线鼠标 `3200.00 JPY`、库存 20。请先查商品列表取得实际 ID，不把 1 当成固定业务规则。

`WELCOME10` 只发给 Alice，一人一份。最低消费 5000，折扣 10%，最多优惠 1000；下单占用，付款后使用，未付款取消后释放。两件键盘的小计为 16000，折扣封顶 1000，最终金额 15000 JPY。

订单响应字段是 `orderNumber`、`subtotal`、`discount`、`totalAmount`、`currency` 等；不是 `number` 或 `total`。订单 ID 是完整 UUID，路径参数不能填 `123`。文档里的省略字段或假设金额必须看作示意，不能与默认数据混用。

本项目为教学统一使用两位小数，不是完整的多币种资金账本；真实通道还需按币种最小货币单位、渠道规则和财务口径设计。

## 5. 三个必须先理解的边界

**事务边界。** 创建订单的幂等记录、优惠券、库存、订单、订单项和 Outbox 一起提交。`flush` 不是提交；全局 `clear` 会让所有已托管对象脱离 JPA 跟踪。默认事务代理只拦截经过代理的调用；退款拆成两个 Bean 是为了避免同类自调用使事务失效。受检异常需要显式回滚规则。

**支付边界。** `FakePaymentGateway` 不发真实支付请求，`timeout/unknown` 是确定性模拟。外部调用在事务外；提供方需要按稳定的 paymentId/refundId 去重。当前没有自动对账任务或真实 HTTP 支付适配器。UNKNOWN 是“结果不知道”，不是拒付：应使用原键查询并核对，不能换新键再付，也不能直接取消释放库存。演示支付参数 `decline` 才是明确拒付。模拟器没有使用配置中的连接/读取超时，不能据此声称已验证真实网络超时。

**消息边界。** 下单产生 `order.created.v1`，生命周期消费者记录审计；支付成功才产生 `order.paid.v1`，随后通知和积分分别消费。Confirm Ack 不等于消费者业务成功；mandatory Return 表示没有路由到队列。去重标记与数据库副作用同事务提交，仍然不是对任意外部副作用的“恰好一次”保证。

缓存仅供展示，可能短暂过期。当前实现用本实例的同键结果复用和最多 8 个并发回源限制数据库压力；繁忙返回 503。Redis 锁也不能把展示缓存变成强一致的订单价格源。

## 6. 更新过旧演示环境时

V001～V003 保持原校验和；新增 V004～V006，而不是改旧迁移。V004 增加一张订单只有一个未明确拒付的支付、一次支付只有一个未明确失败的退款等约束。旧演示库若已有矛盾数据，迁移会拒绝通过；**不要伪造 FAILED/DECLINED 来消除错误**。

刚开始学习且不需要沿用旧演示数据时，可隔离新环境，不删除旧数据卷：

```bash
# 当前目录 mini-commerce；先停止旧项目占用的同一组端口，不加 -v
docker compose --profile app --profile observability down
docker compose -p mini-commerce-study --profile app up -d --build --wait --wait-timeout 180
python3 scripts/smoke.py
```

以后针对这个新环境的 ps/logs/down 都带 `-p mini-commerce-study`。有需要保留的业务数据时先备份并核对后迁移，不采用“删库重来”。只读 MCP 角色初始化也只会在新 PostgreSQL 数据卷首次启动时执行。

## 7. MCP 和安全范围

HTTP 模式必须使用 Bearer Token，本地 stdio 的权限边界是启动进程本身。数据库使用 `commerce_readonly`，只授予 products、inventory、orders、order_items 的 SELECT；不授予账户、密码哈希或 Refresh Token 表的读取权限。应用数据库角色和演示口令不适用于生产。

EXPLAIN 工具输入一条 SELECT/WITH，由工具自行添加 EXPLAIN；不接受用户传入 EXPLAIN ANALYZE。SQL 关键词检查只是一道防误用措施，不是 SQL 沙箱。检索文档经过真实路径校验、防止越出仓库，并始终标为不可信数据。

`run_test_suite` 默认禁止执行，HTTP 模式始终不能开启；只有信任本地仓库时才在 stdio 设置 `MCP_ENABLE_TEST_EXECUTION=true`。固定命令也会执行仓库中的任意测试代码，超时和白名单不等于完整隔离。本地 Docker MCP 镜像也未安装 Java/Maven，不承诺能在该镜像中运行后端测试。

requestId 是入口关联号；traceId 由链路框架管理，两者不能用同一个客户端字符串冒充。消息保存 traceId 字段不代表自动建立了完整的跨 RabbitMQ 父子 Span。

## 8. 验证材料该怎么读

`LearningReadinessIT` 保存本次首先复现的 7 个问题；`BusinessSafetyIT` 验证重试、并发、取消、权限、消息去重和实际配置；`InfrastructureReadinessTest` 验证缓存与 Confirm/Return 边界。初始复现运行号为 `34085970470`，原测试通过而新增 7 项失败，说明文件和格式检查不能代替行为测试。

修复后的第一轮运行 `34087808615` 已验证 Java 36 项、MCP 17 项，未跳过；这是后续文档及容器验收前的中间证据，不冒充最终提交结果。最终以 main 当前提交的 `mini-commerce-ci` 和学习资料门禁为准。

格式检查只证明格式；词典标记检查只证明内容存在；链接检查只证明本地路径存在。当前没有声称完成生产压测、真实支付验证、云上 apply、所有外链可用性检查或全面依赖漏洞扫描。

## 9. 第一天的结束标准

先看[零基础入口](BEGINNER-START-HERE.md)，再看[创建订单走读](REQUEST-TO-DATABASE-WALKTHROUGH.md)。只打开 OrderController、OrderDtos、CreateOrderService、InventoryService、InventoryRepository 五个文件。

第一个 20 分钟只说明“请求从哪里进入、调用谁”；第二个 20 分钟只说明“哪些数据库修改同成同败”；第三个 20 分钟运行一个测试，并说明它在防什么错误。遇到不懂的词查本地词典，写入稍后清单，不同时打开十几个专题。

今天能不看源码讲清楚“请求 → 业务流程 → 条件库存更新 → 数据库事务”，就可以停止。退款、消息租约、MCP 和云不是第一天的要求。
