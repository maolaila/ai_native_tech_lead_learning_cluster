# 模块 09：CI/CD、发布与回滚

> **所属模块：** 09 CI/CD
> **本文用途：** 把代码提交转换为可重复验证、可追踪、可审批和可恢复的发布过程。
> **前置知识：** 测试、数据库、Docker
> **建议投入：** 3 周

---

## 核心链路

```text
Commit / PR
→ Static Checks
→ Unit
→ Integration / API
→ Build Artifact
→ Security Scan
→ Image
→ Staging
→ Migration
→ Smoke / E2E
→ Approval
→ Production
→ Verify / Rollback
```

Jenkins 和 GitHub Actions 只是执行引擎。真正要掌握的是 Artifact、环境、门禁、Secret、Migration 顺序、Release Strategy、Rollback 和审计。

文件：

1. [`01_Pipeline与质量门禁.md`](01_Pipeline与质量门禁.md)
2. [`02_Artifact_环境与Secret.md`](02_Artifact_环境与Secret.md)
3. [`03_Database_Migration发布顺序.md`](03_Database_Migration发布顺序.md)
4. [`04_发布策略与回滚.md`](04_发布策略与回滚.md)
5. [`05_Jenkins与GitHubActions映射.md`](05_Jenkins与GitHubActions映射.md)
6. [`06_实操与验收.md`](06_实操与验收.md)
