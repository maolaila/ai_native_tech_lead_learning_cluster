# Jenkins 与 GitHub Actions 的概念映射

> **所属模块：** 09 CI/CD
> **本文用途：** 把你使用过 Jenkins 的经验迁移为平台无关 Pipeline 能力。
> **前置知识：** Pipeline 原理
> **建议投入：** 阅读 3 小时，配置 5 小时

---

## 概念

| 平台无关 | Jenkins | GitHub Actions |
|---|---|---|
| Pipeline 定义 | Jenkinsfile | workflow YAML |
| 执行单位 | Stage/Step | Job/Step |
| 执行机器 | Agent/Node | Runner |
| Trigger | Webhook/Poll | `on:` |
| Secret | Credentials | Secrets/Environments |
| Artifact | archive/stash | upload/download-artifact |
| 重用 | Shared Library | Reusable Workflow/Action |
| 审批 | Plugin/Input | Environment Protection |

## Jenkins 注意

- Job UI 配置尽量迁入 Jenkinsfile；
- Agent 不应长期共享脏 Workspace/凭证；
- Shared Library 版本化；
- 控制 Script Approval 和 Plugin 风险；
- 不让所有项目共用管理员 Credential。

## GitHub Actions 注意

- 最小 `permissions`；
- 第三方 Action 固定 Commit SHA；
- Fork PR 不获得 Secret；
- 使用 Concurrency 取消旧 Run；
- Environment 审批生产；
- OIDC 获取短期云权限。

## 不要重复平台逻辑

核心命令放仓库脚本：

```bash
./scripts/ci/unit.sh
./scripts/ci/integration.sh
./scripts/ci/build-image.sh
./scripts/ci/smoke.sh
```

Jenkins/GitHub Actions 负责调度。开发者本地也能运行，降低平台锁定。

## CI 与 MCP

MCP 可以只读查询 Pipeline、失败 Job 和 Artifact；重新运行低风险 Job可审批；生产 Deploy/Migration 必须 Human Approval 和审计。
