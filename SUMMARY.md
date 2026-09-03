# 文件集群导航

> 从 `README.md` 开始。这里是全部 Markdown 文件的索引。

## 根目录

- [AI-Native Tech Lead / Architect 学习文件集群](README.md)
- [学习进度总清单](PROGRESS_CHECKLIST.md)
- [从资深前端到 AI-Native Tech Lead / Architect 学习路线](00_原始学习路线.md)

## 后端小白专用入口

- [后端零基础：从这里开始](mini-commerce/docs/BEGINNER-START-HERE.md)
- [一次创建订单请求完整走读](mini-commerce/docs/REQUEST-TO-DATABASE-WALKTHROUGH.md)
- [Spring 与 Java 注解小白词典](mini-commerce/docs/SPRING-JAVA-ANNOTATIONS.md)
- [后端专有名词通俗词典](mini-commerce/docs/BACKEND-TERMS-PLAIN-CHINESE.md)
- [Java 后端阅读语法速查](mini-commerce/docs/JAVA-SYNTAX-FOR-BACKEND-BEGINNERS.md)
- [Spring 配置从零开始](mini-commerce/docs/CONFIGURATION-FROM-ZERO.md)
- [ADHD 友好的学习计划](mini-commerce/docs/ADHD-FOCUSED-LEARNING-PLAN.md)
- [后端小白常见问题](mini-commerce/docs/BEGINNER-FAQ.md)

## `00_start`

- [总路线与使用方法](00_start/01_总路线与使用方法.md)
- [长期项目：Mini Commerce](00_start/02_长期项目_Mini_Commerce.md)
- [48 周执行计划](00_start/03_48周执行计划.md)
- [环境与版本基线](00_start/04_环境与版本基线.md)
- [阶段门与复盘](00_start/05_阶段门与复盘.md)

## `01_foundations`

- [HTTP 请求全链路](01_foundations/01_HTTP请求全链路.md)
- [Linux：进程、端口、权限与日志](01_foundations/02_Linux进程端口权限日志.md)
- [网络基础与排障](01_foundations/03_网络与排障.md)
- [基础实操与验收](01_foundations/04_实操与验收.md)
- [模块 01：HTTP、Linux 与网络基础](01_foundations/README.md)

## `02_backend_spring`

- [Spring 请求生命周期与 IoC / DI](02_backend_spring/01_请求生命周期与IoC_DI.md)
- [Controller、Service、Repository 分层](02_backend_spring/02_Controller_Service_Repository分层.md)
- [DTO、Entity、Domain 与映射](02_backend_spring/03_DTO_Entity_Domain与映射.md)
- [API 设计、校验、异常与错误码](02_backend_spring/04_API设计_校验_异常与错误码.md)
- [日志、配置与健康检查](02_backend_spring/05_日志_配置与健康检查.md)
- [订单模块：从需求到代码](02_backend_spring/06_订单模块案例.md)
- [后端实操与验收](02_backend_spring/07_实操与验收.md)
- [模块 02：Spring Boot 后端工程](02_backend_spring/README.md)

## `03_testing`

- [测试思维：从手点到可重复验证](03_testing/01_测试思维与可重复验证.md)
- [测试用例设计：边界、状态、权限、失败与并发](03_testing/02_测试用例设计.md)
- [后端单元测试：JUnit、AssertJ、Mockito](03_testing/03_后端单元测试.md)
- [前端单元与组件测试](03_testing/04_前端单元与组件测试.md)
- [集成测试：Spring Boot、Testcontainers 与 PostgreSQL](03_testing/05_集成测试与Testcontainers.md)
- [API 与契约测试](03_testing/06_API与契约测试.md)
- [Playwright E2E](03_testing/07_Playwright_E2E.md)
- [回归测试、覆盖率与测试金字塔](03_testing/08_回归_覆盖率与测试金字塔.md)
- [AI 生成测试的审查与 Eval](03_testing/09_AI生成测试的审查与Eval.md)
- [测试实操与验收](03_testing/10_实操与验收.md)
- [模块 03：从人工点击到系统化测试](03_testing/README.md)

## `04_database_postgresql`

- [关系模型、SQL 与表关系](04_database_postgresql/01_关系模型_SQL与表关系.md)
- [约束、范式与数据建模](04_database_postgresql/02_约束_范式与数据建模.md)
- [索引、B-Tree、复合索引与 EXPLAIN](04_database_postgresql/03_索引与EXPLAIN.md)
- [事务、ACID 与 Spring 事务边界](04_database_postgresql/04_事务与Spring边界.md)
- [并发、锁与库存超卖](04_database_postgresql/05_并发_锁与库存超卖.md)
- [隔离级别、MVCC 与死锁](04_database_postgresql/06_隔离_MVCC与死锁.md)
- [连接池、Migration 与备份恢复](04_database_postgresql/07_连接池_Migration与备份.md)
- [慢 SQL 诊断与优化流程](04_database_postgresql/08_慢SQL诊断流程.md)
- [数据库实操与验收](04_database_postgresql/09_实操与验收.md)
- [模块 04：PostgreSQL、事务与并发](04_database_postgresql/README.md)

## `05_auth_security`

- [Session、Cookie 与 Token 生命周期](05_auth_security/01_Session_Cookie_Token.md)
- [RBAC 与对象级权限](05_auth_security/02_RBAC与对象级权限.md)
- [Web 常见攻击与防御](05_auth_security/03_Web常见攻击.md)
- [Secret、依赖与软件供应链](05_auth_security/04_Secret与供应链.md)
- [安全实操与验收](05_auth_security/05_实操与验收.md)
- [模块 05：认证、授权与应用安全](05_auth_security/README.md)

## `06_redis`

- [Redis 数据类型与使用边界](06_redis/01_数据类型与边界.md)
- [Cache Aside、TTL 与缓存失效](06_redis/02_CacheAside_TTL与失效.md)
- [缓存穿透、热点击穿、雪崩与一致性](06_redis/03_穿透_击穿_雪崩与一致性.md)
- [限流、Session、计数与分布式锁](06_redis/04_限流_Session与分布式锁.md)
- [Redis 实操与验收](06_redis/05_实操与验收.md)
- [模块 06：Redis 与缓存设计](06_redis/README.md)

## `07_rabbitmq`

- [同步、异步与事件边界](07_rabbitmq/01_同步异步与事件边界.md)
- [Exchange、Queue、Binding 与 Routing](07_rabbitmq/02_Exchange_Queue_Routing.md)
- [Publisher Confirm、Ack、Retry 与 DLQ](07_rabbitmq/03_Confirm_Ack_Retry_DLQ.md)
- [幂等、Transactional Outbox 与重复消息](07_rabbitmq/04_幂等与Outbox.md)
- [消息契约、顺序、积压与演进](07_rabbitmq/05_消息契约_顺序与积压.md)
- [RabbitMQ 实操与验收](07_rabbitmq/06_实操与验收.md)
- [模块 07：RabbitMQ 与可靠异步处理](07_rabbitmq/README.md)

## `08_runtime_deployment`

- [镜像、容器与 Dockerfile](08_runtime_deployment/01_镜像_容器与Dockerfile.md)
- [Compose、Network、Volume 与 Health Check](08_runtime_deployment/02_Compose_Network_Volume_Health.md)
- [配置、Secret 与环境分离](08_runtime_deployment/03_配置_Secret与环境.md)
- [进程、资源限制与优雅关闭](08_runtime_deployment/04_进程_资源与优雅关闭.md)
- [反向代理、TLS 与部署网络排障](08_runtime_deployment/05_反向代理_TLS与排障.md)
- [运行与部署实操验收](08_runtime_deployment/06_实操与验收.md)
- [模块 08：Docker、Linux 与应用运行](08_runtime_deployment/README.md)

## `09_cicd`

- [Pipeline、质量门禁与反馈速度](09_cicd/01_Pipeline与质量门禁.md)
- [Artifact、环境与 Secret](09_cicd/02_Artifact_环境与Secret.md)
- [数据库 Migration 与应用发布顺序](09_cicd/03_Database_Migration发布顺序.md)
- [发布策略、验证与回滚](09_cicd/04_发布策略与回滚.md)
- [Jenkins 与 GitHub Actions 的概念映射](09_cicd/05_Jenkins与GitHubActions映射.md)
- [CI/CD 实操与验收](09_cicd/06_实操与验收.md)
- [模块 09：CI/CD、发布与回滚](09_cicd/README.md)

## `10_observability`

- [结构化日志与关联 ID](10_observability/01_结构化日志与关联ID.md)
- [Metrics、RED/USE 与延迟百分位](10_observability/02_Metrics_RED_USE与百分位.md)
- [Distributed Tracing 与上下文传播](10_observability/03_Tracing与上下文传播.md)
- [SLI、SLO、Error Budget 与告警](10_observability/04_SLI_SLO与告警.md)
- [Incident 响应与生产 Debug 流程](10_observability/05_Incident响应与Debug流程.md)
- [可观测性故障演练与验收](10_observability/06_故障演练与验收.md)
- [模块 10：可观测性与生产故障处理](10_observability/README.md)

## `11_system_design`

- [需求、约束与业务建模](11_system_design/01_需求_约束与业务建模.md)
- [模块化单体、依赖方向与微服务边界](11_system_design/02_模块化单体与边界.md)
- [数据库、缓存、队列、对象存储、CDN 与搜索的选型](11_system_design/03_技术组件选型.md)
- [Timeout、Retry、Backoff、Circuit Breaker 与 Bulkhead](11_system_design/04_韧性_Timeout_Retry_Circuit.md)
- [扩展性、容量估算与瓶颈](11_system_design/05_扩展性_容量与瓶颈.md)
- [ADR、架构规则与治理](11_system_design/06_ADR与架构治理.md)
- [系统设计案例：会员订阅与权益](11_system_design/07_会员订阅系统案例.md)
- [系统设计实操与验收](11_system_design/08_实操与验收.md)
- [模块 11：业务建模与系统设计](11_system_design/README.md)

## `12_cloud_aws`

- [云服务心智模型与架构映射](12_cloud_aws/01_云服务心智模型与架构映射.md)
- [IAM、Role、Policy 与最小权限](12_cloud_aws/02_IAM与最小权限.md)
- [VPC、Subnet、Security Group 与互联网入口](12_cloud_aws/03_VPC_网络与入口.md)
- [计算、对象存储、RDS 与容器部署](12_cloud_aws/04_计算_存储_数据库与部署.md)
- [AWS 成本、安全、备份与实操验收](12_cloud_aws/05_成本_备份_安全与验收.md)
- [模块 12：AWS 基础与云上运行](12_cloud_aws/README.md)

## `13_ai_engineering_mcp`

- [把隐性经验变成 Docs as Code](13_ai_engineering_mcp/01_把隐性经验变成DocsAsCode.md)
- [Rules、Guardrails 与自动执行](13_ai_engineering_mcp/02_Rules与Guardrails.md)
- [Golden Path、Skills 与模板](13_ai_engineering_mcp/03_GoldenPath_Skills与模板.md)
- [MCP 概念、Host/Client/Server 与边界](13_ai_engineering_mcp/04_MCP概念与架构.md)
- [MCP Tool 设计与契约](13_ai_engineering_mcp/05_MCP工具设计与契约.md)
- [公司 MCP 能力分层设计](13_ai_engineering_mcp/06_公司MCP能力分层.md)
- [权限、沙箱、审批、Prompt Injection 与审计](13_ai_engineering_mcp/07_权限_沙箱_审批与审计.md)
- [AI Coding Eval 数据集、指标与实验设计](13_ai_engineering_mcp/08_Eval数据集与指标.md)
- [新人 + AI 的标准开发工作流](13_ai_engineering_mcp/09_新人AI开发工作流.md)
- [AI Engineering / MCP 实操与验收](13_ai_engineering_mcp/10_实操与验收.md)
- [模块 13：AI Engineering、Rules、Golden Path 与 MCP](13_ai_engineering_mcp/README.md)

## `14_capstone`

- [Phase 1：业务建模、前后端与 CRUD](14_capstone/01_Phase1_业务与CRUD.md)
- [Phase 2：分层自动化测试](14_capstone/02_Phase2_测试体系.md)
- [Phase 3：事务、索引、锁与并发](14_capstone/03_Phase3_事务_索引与并发.md)
- [Phase 4：认证授权、安全、Redis 与 RabbitMQ](14_capstone/04_Phase4_安全_缓存与消息.md)
- [Phase 5：容器、CI/CD、发布与云](14_capstone/05_Phase5_运行_CICD与云.md)
- [Phase 6：可观测性、SLO 与事故演练](14_capstone/06_Phase6_可观测与故障演练.md)
- [Phase 7：Rules、Golden Path、MCP 与新人对照实验](14_capstone/07_Phase7_AI平台与新人实验.md)
- [毕业答辩、评分 Rubric 与六项考试](14_capstone/08_毕业答辩与评分.md)
- [前 90 天启动计划](14_capstone/09_前90天启动计划.md)
- [模块 14：Mini Commerce 毕业项目](14_capstone/README.md)

## `15_templates`

- [Feature Spec：<功能名>](15_templates/01_功能规格_FeatureSpec.md)
- [Test Plan：<功能名>](15_templates/02_测试计划.md)
- [ADR-XXX：<决策标题>](15_templates/03_ADR.md)
- [Code Review Checklist](15_templates/04_CodeReview_Checklist.md)
- [Database Migration Review](15_templates/05_DatabaseMigration_Review.md)
- [Release & Rollback Checklist](15_templates/06_发布与回滚_Checklist.md)
- [Incident Report：<标题>](15_templates/07_Incident_Report.md)
- [Runbook：<问题/操作>](15_templates/08_Runbook.md)
- [Threat Model：<系统/功能>](15_templates/09_ThreatModel.md)
- [AI Task Contract：<任务>](15_templates/10_AI任务契约.md)
- [MCP Tool Spec：<tool_name>](15_templates/11_MCP_Tool_Spec.md)
- [AI Eval Case：<ID>](15_templates/12_AI_Eval_Case.md)
- [Week <N>：<主题>](15_templates/13_每周学习复盘.md)
- [Module Gate：<模块>](15_templates/14_模块阶段门.md)
- [可复制模板目录](15_templates/README.md)

## `16_references`

- [官方文档索引](16_references/01_官方文档索引.md)
- [核心术语表](16_references/02_核心术语表.md)
- [命令与排障速查](16_references/03_命令与排障速查.md)
- [常见误区与暂缓学习清单](16_references/04_常见误区与暂缓学习清单.md)
- [参考资料与速查](16_references/README.md)

## `practice`

- [可执行实验材料](practice/README.md)
- [PostgreSQL 双会话死锁实验](practice/sql/06_deadlock_lab.md)
- [Order Test Matrix](practice/testing/order-test-matrix.md)

## 汇总与校验

- [完整合并版](FULL_BOOK.md)
- [文件清单与校验摘要](MANIFEST.md)
