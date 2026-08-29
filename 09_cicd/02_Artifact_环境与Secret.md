# Artifact、环境与 Secret

> **所属模块：** 09 CI/CD
> **本文用途：** 确保从测试到生产部署的是同一可追踪产物，并控制环境凭证。
> **前置知识：** Docker、安全
> **建议投入：** 阅读 3 小时，实践 5 小时

---

## 一、Build Once, Promote

```text
Source Commit
→ Image Digest sha256:...
→ Staging
→ Production（同一 Digest）
```

若生产重新 Build，依赖仓库和标签变化可能让生产不是 Staging 验证过的内容。

## 二、Artifact 身份

记录：Commit SHA、Build ID、Toolchain、创建时间、SBOM、Image Digest、测试报告和签名/来源。

不要仅用 `v1.2` 或 `latest` 作为唯一身份。

## 三、环境

Local、CI、Staging、Production。环境差异应主要是配置、规模和外部端点，不能是完全不同的代码路径。

Staging 不是生产的绝对复制，但应覆盖关键：数据库类型、Migration、认证、队列、代理、Observability。

## 四、Secret 注入

CI Secret Store / Environment Secret；最小权限；短期凭证优于长期 Key；敏感 Job 限制 Branch/Environment；Mask 不是万能，脚本也不能 Echo。

## 五、OIDC 与短期云凭证

CI 可通过身份联合获取短期 Role，避免长期 AWS Key。权限仅部署所需资源，并限定 Repository/Branch/Environment。

## 六、PR 安全

Fork/未信任 PR 不应获取生产 Secret。不要在高权限上下文执行可被 PR 修改的脚本。

## 七、Artifact Retention

保留当前、上一稳定和审计所需版本；保证回滚 Artifact 仍在。设置生命周期和存储成本。

## 八、配置验证

发布前校验必填、类型、URL、Secret 引用和 Feature Flag。配置错误也应经过 Change Review 和审计。
