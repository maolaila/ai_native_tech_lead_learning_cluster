# Phase 5：容器、CI/CD、发布与云

> **所属模块：** 14 Capstone
> **本文用途：** 把项目变成可复制 Artifact，并完成 Staging/生产模拟和恢复。
> **前置知识：** Phase 4、Runtime/CI/Cloud
> **建议投入：** 4～6 周

---

## Runtime

前后端多阶段 Image、非 root、Compose、Network/Volume/Health、Graceful Shutdown、Reverse Proxy/TLS。

## CI

PR：Lint/Type/Unit/Integration/API/Arch/Security；Main：Image、Staging、Smoke；Nightly：Regression/Performance/Restore。

## Artifact

Commit SHA、Image Digest、SBOM、Test Report；Build Once Promote。

## Migration

独立 Job、Expand-Contract、Lock/Statement Timeout、旧新版本兼容。

## Release

Rolling 或 Canary；Feature Flag；Stop Conditions；Approval；Rollback Runbook。

## Cloud

可选 AWS：ALB→ECS/Fargate→RDS→S3；IAM Role、Private DB、Secrets、Cloud Logs/Metrics；Budget。

## 演练

坏镜像、坏配置、Migration Lock、一个实例死亡、DB 连接阻断、回滚、恢复 RDS/本地数据库。

## 输出

Pipeline、Artifact Manifest、Deploy/Release/Recovery 文档、IAM Matrix、Cloud Diagram、Cost Estimate。
