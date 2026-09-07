# 开学前修订记录与验证证据

这份记录回答两个问题：这次到底修了什么，以及什么证据能支持“可以开始本地学习”。它不把文件数量、注释数量或格式检查当成业务正确性的证明。

**开始学习只需要先打开 [正式学习说明](LEARNING-READINESS.md)，不要先读完本报告和全部测试。**

## 1. 本轮已经修正的重点

| 原来的问题或容易误解的地方 | 现在怎样处理 | 对照源码或验证位置 |
|---|---|---|
| Java 类挤成几行，中文说明泛泛而谈 | 保持统一格式；关键类写实际业务职责、原因与章节位置 | `backend/src/main/java`、注解使用索引 |
| 入门图把 Redis、RabbitMQ、测试都画成每个请求的必经步骤 | 请求主线与辅助组件分开；测试属于开发验证 | [零基础入口](BEGINNER-START-HERE.md) |
| UUID 路径示例使用 123；订单返回字段和币种与真实工程不一致 | 区分数字商品 ID 与 UUID 订单 ID；使用真实字段与演示币种 | [HTTP 请求集](../api/mini-commerce.http)、[配置与启动说明](LEARNING-READINESS.md) |
| 把事务解释成“任何错误都会撤销一切” | 说明代理、默认回滚规则、外部调用与并发边界 | [注解词典](SPRING-JAVA-ANNOTATIONS.md)、`InventoryService` |
| 把普通 @Value 与带单位的 Duration 绑定混为一谈 | @Value 用整数毫秒示例；成组带单位配置用 ConfigurationProperties | [配置词典](CONFIGURATION-FROM-ZERO.md)、`AppProperties` |
| 部分 SQL 执行后清空 JPA 跟踪，导致返回成功但后续状态未落库 | 保留必要 flush，不全局 clear；测试再查实际数据库 | `InventoryRepository`、`LearningReadinessIT` |
| 未决支付换新 Key、取消竞争、退款自调用与越权风险 | 订单锁、唯一约束、稳定支付 ID；退款拆开真实事务与外部调用；重放仍鉴权 | `PaymentTransactionService`、`RefundService`、`BusinessSafetyIT` |
| 缓存失败处理可能再次执行数据库查询 | Redis 失败不重复执行同一次业务查询；同键复用结果并限制并发回源 | `ProductCacheService`、`InfrastructureReadinessTest` |
| Broker Ack 被误认为已成功投递到业务队列 | 同时检查 Confirm 与 mandatory Return；过期发布者不能覆盖新租约结果 | `OutboxPublisher`、`OutboxJdbcRepository` |
| 消费者失败可能留下去重标记 | 去重记录与通知/积分在同一事务；故障回滚、重复投递分别测试 | `OrderPaidConsumers`、`BusinessSafetyIT` |
| MCP SQL、文档路径、权限和审计说明过度承诺 | 检查真实只读授权、路径边界与 HTTP 身份；明确不等于完整沙箱 | `mcp-server/tests`、`scripts/check_mcp_runtime.py` |
| 文档站输出路径可能覆盖源码，旧生成器可能重新覆盖修复 | 输出目录保护；停用历史生成与自动提升工作流；main CI 只读校验 | `tools/tests/test_docs_safety.py`、`.github/workflows` |
| 订单指标名称与真实导出不一致；P95 图没有桶数据 | 真实导出器测试、提交后计数、打开 HTTP 直方图；运行时查询 Prometheus | `InfrastructureReadinessTest`、`scripts/check_observability.py` |
| 低流量错误率被错误分母低估，失败告警误称积压告警 | 按实际请求速率相除；明确失败次数不是积压长度 | `infra/observability/alerts.yml`、[监控说明](observability.md) |
| 恢复脚本复用固定库名并清理已有表 | 每次创建随机临时库；仅删除本次成功创建的库；恢复错误立即停止 | `scripts/backup.sh`、`scripts/restore-test.sh` |
| 命令通过管道把结果交给 tee 时，前半段失败可能被掩盖 | 流水线显式使用 Bash 的 pipefail，前半段失败也使该步骤失败 | `.github/workflows/pre-study-audit.yml`、`mini-commerce-ci.yml` |

表中的短路径以 mini-commerce 为根目录；tools 和 .github 指仓库根目录。第一次只看下单相关行，其他内容随文档推进。

## 2. 已取得的真实验收基准

[完整容器验收运行 34095886873](https://github.com/maolaila/ai_native_tech_lead_learning_cluster/actions/runs/34095886873) 的 verify 作业已完成且为 success。其附件中的 `source-commit.txt` 指向 `63d38467e28531cb3a515e3db9474ab022dc7161`，这是该轮**实际测试的源码**，不只看触发工作流的父提交。

原始 XML 统计：Java 单元及架构测试 14 项、真实 PostgreSQL 集成测试 28 项、MCP 测试 17 项，失败、错误、跳过均为 0。该轮还通过了 9 项文档工具测试、静态规则检查、严格文档构建和 Terraform 静态校验。

运行级证据不只是构建了镜像：启动 PostgreSQL、Redis、RabbitMQ、后端、MCP 和监控组件后，执行注册/登录、商品上架、下单重试、付款重试、查询实际订单状态、RabbitMQ 通知及退款重试。MCP 验证匿名拒绝、认证初始化、只读表授权、实际 Schema/EXPLAIN 和审计写入。监控验证真实 Counter、HTTP 直方图桶及 Prometheus 抓取结果。

本页新增的 HTTP 示例校验和安全恢复演练是在这个基准之后加入的，**不把旧运行号冒充它们的验证结果**。后续提交必须重新通过下面的 main CI；原始附件与终端结果才是对应提交的证据。

## 3. 怎样确认你正在学习的版本

日常使用 `main`，不需要在多个修复分支之间切换。仓库的 Actions 中，检查当前 main 提交的两条流水线：

- `mini-commerce-ci`：源码一致性、Java 测试、MCP 测试、完整 Compose/HTTP/消息/监控与恢复演练、Terraform。
- `Beginner-friendly learning quality gate`：Java 格式、文档及索引同步、注解与示例契约、文档站构建。

必须是 **completed + success**；in_progress 表示还在跑，skipped 表示没有执行，都不是“已通过”。`tools/check_test_evidence.py` 还会拒绝没有执行关键集成测试、零测试或有跳过的情况。

要查看本地版本，在仓库根目录执行 `git log -1 --oneline`。目录存在、报告写了“通过”、或者旧提交有绿勾，都不能证明一个新提交也通过了。

## 4. 备份与恢复实验不是第一天任务

学到数据库备份时，在 mini-commerce 目录执行：

```bash
DUMP=$(bash scripts/backup.sh)
bash scripts/restore-test.sh "$DUMP"
```

备份写进 `backups/`，不应提交 Git。恢复演练只用你信任的本地备份；它会创建新临时库并在退出时清理，不清空原业务库。自定义 Compose 项目名时先设置相同的 `COMPOSE_PROJECT_NAME`，例如 `export COMPOSE_PROJECT_NAME=mini-commerce-study`，避免操作错项目。

这验证的是本地逻辑备份可恢复并能查询订单，不等于验证了跨版本恢复、异地灾备或所有业务数据的完整一致性。

## 5. 不能把哪些内容当成已经实现

支付和退款仍是模拟器，不会扣真实的钱；不包含真实通道、自动对账、部分退款、退货和积分冲正。Kubernetes/AWS 是参考模板与静态校验，没有为你创建云资源。MCP 的关键词与路径检查不是操作系统级沙箱。监控不是完整跨消息链路验收，也没有做生产级容量压测或全面依赖漏洞扫描。

原始文档里的阶段门、SLO、前端与 AI 对照实验，仍包含需要你亲自完成的学习任务。章节映射帮助找代码，不能替代逐项功能验收。

## 6. 今天从这里停下检查，开始学习

先按 [正式学习说明](LEARNING-READINESS.md) 启动，再读 [零基础入口](BEGINNER-START-HERE.md) 和 [创建订单走读](REQUEST-TO-DATABASE-WALKTHROUGH.md)。第一次最多打开 5 个业务文件；陌生注解查项目里的词典。

今天的目标只是能讲清楚：请求在哪里进来、订单为什么由后端计价、库存怎样避免负数、重复请求为什么不会再生成一笔订单。不需要第一天掌握云、退款、消息租约或 MCP。
