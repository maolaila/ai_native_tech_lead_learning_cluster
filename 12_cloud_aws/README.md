# 模块 12：AWS 基础与云上运行

> **所属模块：** 12 Cloud
> **本文用途：** 把已有运行、网络、数据和安全概念映射到 AWS，不把云服务当魔法。
> **前置知识：** Docker、CI/CD、Observability、Security
> **建议投入：** 3～5 周基础

---

## 学习目标

达到能设计和 Review 中小型系统云上基线：

```text
Route 53 / CloudFront
→ ALB
→ ECS/Fargate 或 EC2
→ RDS PostgreSQL
→ ElastiCache Redis
→ S3
→ CloudWatch / OpenTelemetry
→ IAM / KMS / Secrets Manager
```

第一阶段不要求 Kubernetes/EKS。

文件：

1. [`01_云服务心智模型与架构映射.md`](01_云服务心智模型与架构映射.md)
2. [`02_IAM与最小权限.md`](02_IAM与最小权限.md)
3. [`03_VPC_网络与入口.md`](03_VPC_网络与入口.md)
4. [`04_计算_存储_数据库与部署.md`](04_计算_存储_数据库与部署.md)
5. [`05_成本_备份_安全与验收.md`](05_成本_备份_安全与验收.md)
