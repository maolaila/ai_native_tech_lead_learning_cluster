# 模块 10：可观测性与生产故障处理

> **所属模块：** 10 Observability
> **本文用途：** 用 Logs、Metrics、Traces 和业务不变量理解系统内部状态，并形成 Incident 闭环。
> **前置知识：** 运行环境、CI/CD
> **建议投入：** 4 周

---

## 为什么不是“把日志打印多一点”

Monitoring 回答已知问题是否发生；Observability 通过系统输出帮助调查未预先想到的问题。

```text
Metrics：发生了什么、规模多大
Traces：慢/错在哪一段
Logs：为什么、具体上下文
Business Signals：用户和数据是否正确
```

文件：

1. [`01_结构化日志与关联ID.md`](01_结构化日志与关联ID.md)
2. [`02_Metrics_RED_USE与百分位.md`](02_Metrics_RED_USE与百分位.md)
3. [`03_Tracing与上下文传播.md`](03_Tracing与上下文传播.md)
4. [`04_SLI_SLO与告警.md`](04_SLI_SLO与告警.md)
5. [`05_Incident响应与Debug流程.md`](05_Incident响应与Debug流程.md)
6. [`06_故障演练与验收.md`](06_故障演练与验收.md)
