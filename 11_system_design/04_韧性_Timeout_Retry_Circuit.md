# Timeout、Retry、Backoff、Circuit Breaker 与 Bulkhead

> **所属模块：** 11 System Design
> **本文用途：** 防止单个慢依赖耗尽全系统，并避免重试风暴。
> **前置知识：** 运行和可观测性
> **建议投入：** 阅读 5 小时，故障实验 6 小时

---

## 一、Timeout 是必须的

没有 Timeout 的外部调用可能永久占线程/连接。分别设置 Connect、Read 和总体业务 Deadline。

## 二、Retry 只适合瞬时且安全

读取通常更易重试；写操作必须幂等或有幂等键。

不要对 Validation、401、404、确定性业务冲突重试。

## 三、指数退避和 Jitter

```text
100ms, 200ms, 400ms, 800ms + random
```

避免所有实例同步冲击恢复中的依赖。

## 四、重试放大

Gateway 3 次 × Service 3 次 × Client 3 次 = 最坏 27 次。明确只有一层负责主要重试，并把总时间纳入 Deadline。

## 五、Circuit Breaker

失败率超过阈值后 Open，快速失败/降级；等待后 Half-Open 少量探测；恢复后 Close。

不能修复依赖，只是保护调用者资源。

## 六、Bulkhead

不同依赖使用独立线程池/连接/并发限制，防止报表接口占满所有资源，拖垮订单。

## 七、Rate Limit / Load Shedding

接近饱和时拒绝低优先流量比接受后全部超时更健康。返回 429/503 和可重试语义。

## 八、Fallback

可返回缓存商品介绍；不能伪造支付成功、余额或权限。降级必须保持业务正确。

## 九、Idempotency

重试写操作前设计：Key、Fingerprint、状态、结果、TTL、并发和持久化。

## 十、Deadline 传播

下游剩余时间少于其最小处理成本时应快速失败。不要每一层重新给完整 5 秒。

## 十一、测试

外部 5s、50% 503、连接拒绝、响应丢失、Slow Recovery；观察线程、池、P99、重试数、Circuit 状态和业务结果。
