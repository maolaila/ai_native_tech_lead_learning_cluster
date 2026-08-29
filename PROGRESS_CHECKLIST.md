# 学习进度总清单

> 用途：只记录“是否通过阶段门”，不要把“读过”当成“掌握”。详细周计划见 `00_start/03_48周执行计划.md`。

## 使用规则

每个模块只有同时具备以下证据才打勾：

- [ ] 能不用搜索解释核心原理；
- [ ] 有可运行实现；
- [ ] 有自动测试；
- [ ] 做过至少一次故障实验；
- [ ] 保存了日志、指标、执行计划或截图证据；
- [ ] 写过一次复盘；
- [ ] 能 Review AI 或新人的错误实现。

## 主线阶段

- [ ] 00 起步：环境、长期项目、学习方法和阶段门
- [ ] 01 Foundations：HTTP、Linux、网络和基础排障
- [ ] 02 Backend：Spring Boot、分层、DTO、API、日志和订单模块
- [ ] 03 Testing：测试设计、Unit、Integration、API、E2E、Regression、AI Test Eval
- [ ] 04 Database：建模、索引、事务、锁、MVCC、死锁、连接池、Migration、恢复
- [ ] 05 Security：认证、授权、对象级权限、Web 安全、Secret 和供应链
- [ ] 06 Redis：数据结构、Cache Aside、一致性、热点、限流、Session 和锁边界
- [ ] 07 RabbitMQ：路由、Confirm/Ack、Retry/DLQ、幂等、Outbox 和契约演进
- [ ] 08 Runtime：Docker、Compose、配置、优雅停机、反向代理和 TLS
- [ ] 09 CI/CD：质量门禁、Artifact、Migration、发布策略和回滚
- [ ] 10 Observability：Logs、Metrics、Traces、SLI/SLO、告警和 Incident
- [ ] 11 System Design：业务建模、模块边界、选型、韧性、容量和 ADR
- [ ] 12 Cloud：AWS 映射、IAM、VPC、计算、存储、数据库、成本和灾备
- [ ] 13 AI Engineering：Docs as Code、Rules、Guardrails、Golden Path、MCP、Eval
- [ ] 14 Capstone：七阶段毕业项目与答辩

## 六个关键毕业考试

### Backend

- [ ] 只给“实现订单模块”，能独立设计 Controller、Service、Repository、DTO、Entity、异常和校验。

### Database

- [ ] 能复现并解释库存超卖，比较原子 UPDATE、乐观锁和悲观锁。

### Testing

- [ ] 面对优惠券需求，主动设计 Unit、Integration、API、E2E 和 Regression Test。

### Production

- [ ] 接口从 100ms 变 3s 时，能按 Metrics → Traces → Logs → DB/External Dependency 定位。

### Architecture

- [ ] 面对会员系统，先讨论 Domain、状态、数据流、一致性、权限和失败，而不是先选框架。

### AI Engineering

- [ ] 新人借助 Rules、Skills、MCP 和自动验证完成常规功能，且危险操作受审批和审计控制。

## 最终交付证据

- [ ] 架构文档和领域模型
- [ ] 数据库 ER 图、Migration 和索引实验报告
- [ ] 测试策略、用例矩阵和 CI 报告
- [ ] 结构化日志、Dashboard、Trace 和告警规则
- [ ] Runbook、事故复盘和恢复演练
- [ ] AI Rules、Golden Path、MCP Tool Spec
- [ ] 至少 20 个 AI Eval Case
- [ ] 一次新人 + AI 对照实验
