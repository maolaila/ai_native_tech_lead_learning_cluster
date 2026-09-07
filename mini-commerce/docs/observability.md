# 可观测性

入口生成 `X-Request-Id` 并写入 MDC；订单、支付和消息使用业务 ID/eventId。Actuator/Micrometer 暴露 RED、JVM、Hikari 与业务 Counter；OTLP Trace 进入 Collector/Tempo。

排障顺序：确认用户影响 → 最近发布/Migration → RED/SLO → Trace 最长或错误 Span → 日志上下文 → DB 锁/连接池/SQL → Redis/MQ/支付依赖 → 数据不变量。

禁止把 userId、orderId、traceId 作为 Prometheus Label；高基数上下文进入日志或 Trace。

## 实现边界

requestId 是本次入口关联号，traceId 由 Micrometer Tracing 管理，不能拿客户端的 X-Request-Id 覆盖。Outbox 里保存 traceId 并不自动建立跨消息的父子 Span。local 暴露 Prometheus 抓取端点且主机端口绑定本地；其他环境需要独立的管理网络和机器身份。Counter 不是业务数据库账本；失败告警看时间窗口内的增量，不用累计失败数大于零永久告警。
