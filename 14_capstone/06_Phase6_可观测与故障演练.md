# Phase 6：可观测性、SLO 与事故演练

> **所属模块：** 14 Capstone
> **本文用途：** 证明系统上线后能被理解、告警、止血和恢复。
> **前置知识：** Phase 5、Observability
> **建议投入：** 4 周

---

## Stack

Structured Logs + traceId/orderId/eventId；Micrometer/Prometheus/Grafana；OpenTelemetry/Collector/Trace Backend。

## Dashboard

RED、USE、DB Pool/Slow/Lock、Redis、RabbitMQ、Outbox、Business Invariants、Deploy Annotation。

## SLO

至少：订单 Availability、P99、事件处理 Freshness、数据正确性。定义有效请求分母和 Error Budget。

## Alerts

用户影响优先；Page/Ticket 分级；Owner/Runbook；避免高基数和噪声。

## 7 个 Drill

慢 SQL、池耗尽、Redis 停机、MQ 停机、毒消息、第三方慢、坏发布。

## Incident

每次记录影响、时间线、检测、止血、根因、促成因素、恢复、Action Item。至少一项变成 Regression+Rule+Eval。

## 演示要求

评审者随机触发一个已准备故障，你不能先看源码；从 Dashboard→Trace→Log→DB/MQ 定位并执行 Runbook。
