# Distributed Tracing 与上下文传播

> **所属模块：** 10 Observability
> **本文用途：** 定位跨 API、数据库、缓存、MQ 和外部服务的延迟与错误路径。
> **前置知识：** Logs/Metrics
> **建议投入：** 阅读 5 小时，实践 6 小时

---

## 一、Trace / Span

Trace 表示一次端到端操作；Span 表示其中一段：

```text
POST /orders [Trace]
├─ auth.verify
├─ product.query
├─ inventory.reserve
├─ order.insert
├─ outbox.insert
└─ response.serialize
```

Span 有 parent、start/end、status、attributes 和 events。

## 二、上下文传播

HTTP 使用标准 Trace Context Header；MQ 把上下文放 Message Header。Consumer 通常创建与 Producer 关联的新 Span。

若线程池、异步任务、Reactor 或 MQ 丢上下文，Trace 会断裂。传播需要自动 Instrumentation + 框架正确配置，必要时显式包装。

## 三、Span Attributes

低基数、可诊断：HTTP method/route/status、DB system、Peer service、messaging destination、error type。

不要记录 SQL Secret、Token、完整 Body。orderId 可放 Span 属性用于查询，但注意成本和隐私；通常 Business ID 在日志更合适。

## 四、采样

- Head Sampling：请求开始决定，成本可控但可能丢稀有错误；
- Tail Sampling：收集后按 Error/Latency 决定，诊断强但基础设施更复杂。

初期：保留全部错误/高延迟，正常请求低比例。

## 五、Trace 不能替代 Logs/Metrics

Trace 适合个别请求路径；Metric 适合总体趋势和告警；Log 适合详细事件。三者用 traceId 和 Exemplars 互联。

## 六、数据库 Span

显示 SQL 操作、表/系统、耗时和错误；不要把敏感参数写出。N+1 会在 Trace 中表现为大量重复子 Span。

## 七、MQ Trace

Producer Span 结束不等于 Consumer 立即执行。观察 Publish、Queue Delay、Process Time，并使用 eventId 查重复。

## 八、OpenTelemetry 架构

```text
Application SDK/Agent
→ OTLP
→ Collector
→ Trace/Metric/Log Backend
```

Collector 负责批处理、重试、采样、脱敏、路由，避免每个应用绑定单一后端。

## 九、实验

让 Payment Client 延迟 2 秒，用 Trace 找最长 Span；制造 N+1；制造 Queue 积压，区分 Queue Delay 与 Consumer Processing。
