# 可观测性

入口生成 `X-Request-Id` 并写入 MDC；订单、支付和消息使用业务 ID/eventId。Actuator/Micrometer 暴露 RED、JVM、Hikari 与业务 Counter；OTLP Trace 进入 Collector/Tempo。

排障顺序：确认用户影响 → 最近发布/Migration → RED/SLO → Trace 最长或错误 Span → 日志上下文 → DB 锁/连接池/SQL → Redis/MQ/支付依赖 → 数据不变量。

禁止把 userId、orderId、traceId 作为 Prometheus Label；高基数上下文进入日志或 Trace。

## 实现边界

requestId 是本次入口关联号，traceId 由 Micrometer Tracing 管理，不能拿客户端的 X-Request-Id 覆盖。Outbox 里保存 traceId 并不自动建立跨消息的父子 Span。local 暴露 Prometheus 抓取端点且主机端口绑定本地；其他环境需要独立的管理网络和机器身份。Counter 不是业务数据库账本；失败告警看时间窗口内的增量，不用累计失败数大于零永久告警。

## 先验证“监控真的收到数据”

在 mini-commerce 目录启动 app 和 observability，运行一次 `python3 scripts/smoke.py` 后，执行：

```bash
python3 scripts/check_observability.py
```

检查两层：后端确实导出了订单计数；Prometheus 也确实抓到了它，而不是仅仅网页能打开。
Java 中的名字是 `commerce.orders.creation`；Prometheus 查询名是 `commerce_orders_creation_total`。
名字末尾不要用 `.created`：新 Prometheus Java 客户端保留这个后缀，会将它删掉。
本项目为这个命名写了真实导出器测试，并在完整容器验收中查询实际结果。

计数在订单事务提交后增加；同键重试不重新增加。但程序重启会重置进程内计数，提交后立即宕机也可能漏记，所以它不是“数据库订单总数”。观察近期速率可查询：

```promql
sum(rate(commerce_orders_creation_total[5m]))
```

官方核对：[Micrometer 1.13 指标后缀迁移说明](https://github.com/micrometer-metrics/micrometer/wiki/1.13-Migration-Guide#invalid-meter-suffixes)。本页已给出当前工程需要的用法，不必现在离开仓库阅读。


### P95、Counter 和告警分别在说什么

P95 可以先理解为“这一段时间里，大约 95% 的请求比它快”。它不是平均值，直方图算出的值是估计值。
本项目已打开 `http.server.requests` 的直方图桶。先调用几个接口，等至少两次抓取后再看 Grafana；刚启动时空图不等于程序坏了。

Counter 是“从这次进程启动以来累计发生多少次”。看失败趋势通常用 rate/increase，不直接用累计值永久报警。
错误率等于失败请求速率除以全部请求速率，不能为了避免除零把分母随意改成 1。完全没有请求时，比例没有意义。
Outbox 发布失败告警不是“待发消息积压量”的监测；要监测积压，应另外统计未发布记录数及最老事件等待时间。
