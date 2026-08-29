# MCP 概念、Host/Client/Server 与边界

> **所属模块：** 13 AI Engineering
> **本文用途：** 理解 MCP 在 AI 软件生产体系中的角色，避免把它误解为万能 Agent。
> **前置知识：** Golden Path 基础
> **建议投入：** 阅读 5 小时，最小实验 5 小时

---

## 一、MCP 解决什么

MCP 为 AI Host/Client 与外部 Server 之间提供标准化上下文和工具接口。价值是让 Coding Agent 获取公司特有知识和受控能力，而不是重复内置文件读写。

## 二、角色

```text
Host：Codex/Claude Code/IDE/Agent Platform
  └─ MCP Client：与某 Server 建立会话
       └─ MCP Server：暴露 Resources / Tools / Prompts 等能力
```

具体支持以 Host 当前实现为准。

## 三、能力分类

### Resources

可读取上下文：架构文档、Schema、API、Module Map、Runbook。

### Tools

可执行动作：查询日志、运行测试、检查 Migration、获取 Pipeline。

### Prompts / Workflows

可复用任务模板。不同 Host 对呈现支持不同，因此核心流程也应有普通 Markdown/CLI 形式。

## 四、Transport

本地 Server 常使用 stdio；远程可使用规范支持的 HTTP 类 Transport。远程意味着认证、授权、TLS、租户隔离、审计、超时和可用性。

## 五、MCP 不负责

- 自动理解公司所有业务；
- 判断需求是否正确；
- 取代测试；
- 取代权限；
- 自动保证 Tool 安全；
- 取代 Human Approval；
- 保证所有 Host 行为一致。

## 六、何时不需要 MCP

静态规则写在仓库可直接读取；已有可靠 CLI；通用 Git/文件操作 Host 已支持；一次性脚本；高风险生产操作不应暴露。

## 七、Server 边界

优先按信任域和职责：Knowledge、Engineering、Observability、Database Read-only。不要一个万能 Server 同时读文档、改 IAM、删生产数据。

## 八、返回内容

短、结构化、可追溯，带 source/version/timestamp/environment。不要一次返回 50MB 日志或整个数据库。

## 九、失败语义

Tool 明确区分：输入无效、无权限、依赖不可用、业务冲突、部分成功、超时。Agent 才能决定是否重试、改输入或交给人。

## 十、版本

协议和 SDK 演进较快。Server 启动时记录协议/实现版本，维护兼容矩阵和升级测试。
