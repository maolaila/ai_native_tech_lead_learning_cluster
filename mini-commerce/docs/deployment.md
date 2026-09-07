# 部署、Migration 与回滚

本地使用 Compose；镜像多阶段构建、运行时非 root。生产参考 Kubernetes 清单，但数据库、Redis、RabbitMQ 应使用托管或独立高可用方案。

数据库发布采用 Expand-Contract：先新增兼容结构，再发布兼容代码、分批回填、切读，最后在后续版本删除旧结构。应用镜像可回滚不代表数据可回滚，因此破坏性 Migration 默认前滚修复。

发布停止条件：5xx、P95/P99、订单成功率、Outbox oldest age、支付对账不变量。回滚后执行登录、商品、下单、消息和数据一致性 Smoke。

## 模板不是已部署环境

Kubernetes 清单中的 replace 占位符、外部数据库和 Secret 需要自行配置；只读根文件系统为 /tmp 提供独立卷。AWS Terraform 只执行 fmt/init/validate，不执行 apply。发布、SLO 和回滚步骤是练习目标，不代表已有生产部署证据。旧数据库迁移和不删除旧数据的隔离启动方法见[正式学习说明](LEARNING-READINESS.md)。
