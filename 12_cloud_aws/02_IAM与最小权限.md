# IAM、Role、Policy 与最小权限

> **所属模块：** 12 Cloud
> **本文用途：** 建立人、应用、CI 和 MCP 的身份边界，避免长期管理员凭证。
> **前置知识：** 安全基础
> **建议投入：** 阅读 5 小时，Policy 实验 5 小时

---

## 一、身份类型

- 人员登录：SSO/Identity Center + MFA；
- Workload：IAM Role；
- CI：OIDC 假设 Role；
- 服务间：Task/Instance Role；
- 避免长期 Access Key。

## 二、Policy

```text
Effect
Action
Resource
Condition
```

默认拒绝；显式 Allow；显式 Deny 优先。

## 三、最小权限

不要：`Action:* Resource:*`。

例如 API 只需读取某个 Secret、写某个 S3 Prefix、发送某个 Queue。Migration Role 才有 DDL；应用 Role 不应能管理 IAM。

## 四、Role 与 Credential

ECS Task Role 提供短期凭证，应用 SDK 自动刷新。不要把 AWS Key 放镜像、Git 或环境文件长期保存。

## 五、CI OIDC

GitHub Actions/Jenkins 通过受信身份获得短期部署 Role。Trust Policy 限定 Repository、Branch、Environment、Audience。

## 六、MCP / Agent 权限级别

```text
Level 0：文档和代码只读
Level 1：查询测试/日志/指标
Level 2：创建 Branch/运行非生产 Job
Level 3：Staging 变更，需审批
Level 4：Production 只读
Level 5：Production 写/Deploy/Migration，强审批且默认关闭
```

AI 不因“方便排查”获得 AdministratorAccess。

## 七、权限调试

记录 CloudTrail；使用 Policy Simulator/Access Analyzer；区分 Identity Policy、Resource Policy、Permission Boundary、SCP 和 KMS Policy。

## 八、Key Rotation

长期凭证有 Owner、用途、创建/最后使用、轮换和撤销。发现泄露立即撤销，不只是删除代码。

## 九、Break Glass

紧急高权限账户：MFA、极少人员、默认不使用、访问告警、事后审计。

## 十、验收问题

谁能读生产 Secret？谁能 Deploy？CI 被恶意 PR 修改会怎样？MCP 被 Prompt Injection 诱导后最大破坏范围？
