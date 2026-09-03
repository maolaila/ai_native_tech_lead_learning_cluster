# 可观测性

入口生成 `X-Request-Id` 并写入 MDC；订单、支付和消息使用业务 ID/eventId。Actuator/Micrometer 暴露 RED、JVM、Hikari 与业务 Counter；OTLP Trace 进入 Collector/Tempo。

排障顺序：确认用户影响 → 最近发布/Migration → RED/SLO → Trace 最长或错误 Span → 日志上下文 → DB 锁/连接池/SQL → Redis/MQ/支付依赖 → 数据不变量。

禁止把 userId、orderId、traceId 作为 Prometheus Label；高基数上下文进入日志或 Trace。
