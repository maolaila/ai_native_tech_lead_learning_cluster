# Pipeline、质量门禁与反馈速度

> **所属模块：** 09 CI/CD
> **本文用途：** 设计快反馈和深验证并存的流水线，让坏改动尽早停止。
> **前置知识：** 测试体系
> **建议投入：** 阅读 4 小时，配置 6 小时

---

## 一、CI 的目标

每次改动在合并前被自动构建和验证，减少“只在某人电脑能跑”。CI 不是“有个 Jenkins Job”，而是可信的自动证据。

## 二、从快到慢

```text
Format / Lint / Type Check
→ Unit
→ Build
→ Integration / API
→ Security / Dependency
→ Image
→ E2E Smoke
```

失败越早，等待和算力越少。快检查可并行；Build Artifact 之后被后续 Job 复用。

## 三、PR 与 Main

PR：Lint、Unit、关键 Integration、API Contract、Diff Coverage、基础安全扫描。

Main：完整 Integration、Image、Staging、Smoke、较全 E2E。

Nightly：长回归、性能基线、完整依赖/镜像扫描、备份恢复等。

## 四、Fail Fast 但保留证据

失败时上传：测试报告、Coverage、Playwright Trace、Build Log、扫描报告、Image Digest。只显示“Job failed”不够。

## 五、门禁

- Build/Test 必须通过；
- 新增代码不降低关键覆盖；
- 高危漏洞阻止发布；
- API 破坏性变更需批准；
- Migration Review；
- 架构规则检查；
- 高风险模块需要 Code Owner。

门禁过多且不可靠会被绕过，因此每个 Gate 有明确价值、Owner 和修复路径。

## 六、Flaky

不能无限 Retry 到绿。标记、隔离、分配 Owner、收集失败率并修复。偶发红等于没有门禁。

## 七、缓存

依赖缓存减少时间，但不能让旧 Artifact 混入。Cache Key 包含 Lockfile、工具版本和平台。

## 八、取消过期运行

同一分支新 Commit 到来时取消旧 Pipeline，减少资源和过期结果干扰。

## 九、Pipeline as Code

进入 Git、Review、可回滚。CI 逻辑不应只藏在 Jenkins UI。

## 十、度量

Pipeline P50/P95、失败率、Flaky、首次反馈、队列等待、部署频率、失败变更率、恢复时间。
