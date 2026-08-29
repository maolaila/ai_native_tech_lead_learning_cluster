# Metrics、RED/USE 与延迟百分位

> **所属模块：** 10 Observability
> **本文用途：** 建立低成本趋势和告警信号，避免只看 CPU 或平均响应时间。
> **前置知识：** 基础运行知识
> **建议投入：** 阅读 5 小时，Dashboard 6 小时

---

## 一、Metric 类型

- Counter：只增，如请求总数；
- Gauge：可上下，如 Queue Depth；
- Histogram：分布，如请求耗时；
- Summary：客户端计算分位，聚合限制较多。

## 二、RED

面向服务：

```text
Rate：请求速率
Errors：错误率
Duration：耗时分布
```

按 route/status 分类，但不能把 userId/orderId 作为 Label，否则高基数爆炸。

## 三、USE

面向资源：

```text
Utilization：利用率
Saturation：排队/接近上限
Errors：资源错误
```

应用到 CPU、Memory、Disk、Network、DB Pool、Thread Pool、Queue Consumer。

## 四、平均值欺骗

1000 个请求：990 个 100ms、10 个 10s，平均约 199ms，但最慢用户很差。

看 P50、P95、P99，且明确窗口和流量。分位数不能简单把各实例数值平均，应使用可聚合 Histogram。

## 五、Golden Signals

Latency、Traffic、Errors、Saturation。与 RED/USE 互补。

## 六、业务指标

- 订单创建成功率；
- 支付回调未匹配；
- 库存不变量违规；
- 优惠券重复使用；
- Outbox 最老 Pending；
- DLQ 消息数；
- 缓存回源率。

技术绿不代表业务正确。

## 七、Prometheus Label

低基数：service、route 模板、status、method、environment。

高基数不要做 Label：userId、orderId、traceId、原始 URL、errorMessage。这些放 Logs/Traces。

## 八、Counter Rate

使用 `rate()`/`increase()` 处理重启归零；错误率要用错误 Rate / 总 Rate，不只看绝对数。

## 九、Dashboard 层次

1. Executive/Service Overview；
2. API/Dependency；
3. DB/Pool；
4. Redis/MQ；
5. Business Invariants；
6. Deploy Annotation。

Dashboard 不是越多越好，每张图回答一个调查问题。
