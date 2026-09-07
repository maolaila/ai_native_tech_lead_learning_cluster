# 测试策略：每种证据能说明什么

| 检查 | 本项目的实际证据 | 不能据此声称 |
|---|---|---|
| 单元测试与架构测试 | 金额、订单状态、签名、缓存错误分支、Confirm/Return、分层依赖 | 所有业务流程已成功运行 |
| PostgreSQL 集成测试 | 真实 Flyway/Schema 校验、幂等与并发、支付/退款落库、权限、消费者去重、租约 | Redis 和 RabbitMQ 的网络交互已经被验证 |
| API 契约 | MockMvc 验证 400/401/403/405 等状态；测试不自行包裹事务 | 客户端连接或完整容器启动一定正常 |
| Compose Smoke | 真实容器、注册/登录、专用商品、下单与重放、支付、RabbitMQ 通知、退款 | 完整压测、全部故障组合、真实资金通道 |
| MCP 测试 | 路径与符号链接、拒绝 SQL、脱敏、注入标记、默认禁止执行 | 正则表达式是完整 SQL/提示注入安全证明 |
| Terraform validate | 配置结构与 Provider 约束 | 云资源已创建或网络/IAM 在真实账号可用 |
| 文档门禁 | 本地路径、标记、生成文件一致性、MkDocs 严格构建 | 每句文字都经过形式化验证 |

LearningReadinessIT 首先复现旧版本 7 个缺陷；测试断言数据库最终状态，不能只看 Java 返回对象。BusinessSafetyIT 扩展并发、重放、权限和消息状态验证。

Maven 的 test 运行单元/架构测试；verify 还运行名称为 *IT 的集成测试。CI 先要求 docker info 成功；本地无 Docker 时 Testcontainers 可能显示 skipped，**跳过不是通过**。

覆盖率只是执行痕迹。本仓库没有宣称达到固定覆盖率门槛，也没有完成 DLQ 全故障矩阵或生产压测。具体范围见[正式学习说明](LEARNING-READINESS.md)。
