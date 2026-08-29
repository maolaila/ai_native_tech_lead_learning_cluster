# 模块 13：AI Engineering、Rules、Golden Path 与 MCP

> **所属模块：** 13 AI Engineering
> **本文用途：** 把资深工程经验转化为新人和 Coding Agent 能稳定执行、自动验证且权限受控的软件生产体系。
> **前置知识：** 完成前 12 个模块
> **建议投入：** 持续学习，集中 4～8 周搭第一版

---

## 最终目标

不是“写一个 MCP 就完成”，而是建立：

```text
Business Specification
→ Architecture Docs / Rules
→ Skills / Golden Paths / Templates
→ MCP 提供公司上下文与受控工具
→ Coding Agent 实现
→ Test / Eval / Security / Architecture Gates
→ Human Review / Approval
→ Deploy / Observe / Learn
```

文件：

1. [`01_把隐性经验变成DocsAsCode.md`](01_把隐性经验变成DocsAsCode.md)
2. [`02_Rules与Guardrails.md`](02_Rules与Guardrails.md)
3. [`03_GoldenPath_Skills与模板.md`](03_GoldenPath_Skills与模板.md)
4. [`04_MCP概念与架构.md`](04_MCP概念与架构.md)
5. [`05_MCP工具设计与契约.md`](05_MCP工具设计与契约.md)
6. [`06_公司MCP能力分层.md`](06_公司MCP能力分层.md)
7. [`07_权限_沙箱_审批与审计.md`](07_权限_沙箱_审批与审计.md)
8. [`08_Eval数据集与指标.md`](08_Eval数据集与指标.md)
9. [`09_新人AI开发工作流.md`](09_新人AI开发工作流.md)
10. [`10_实操与验收.md`](10_实操与验收.md)

MCP 协议和具体 Client 支持会持续演进，涉及 Transport、Authorization 或 Host 能力时，以所用 Client 与官方规范当前版本为准。你的核心资产应是业务知识、工具契约、权限和 Eval，而不是绑死某个客户端实现。
