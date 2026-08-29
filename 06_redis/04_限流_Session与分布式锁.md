# 限流、Session、计数与分布式锁

> **所属模块：** 06 Redis
> **本文用途：** 学习非缓存用途，并理解正确性边界。
> **前置知识：** Redis 基础
> **建议投入：** 阅读 4 小时，实践 5 小时

---

## 限流

固定窗口简单但边界可突发；滑动窗口更平滑但成本更高；Token Bucket 可允许突发并控制平均速率。

维度：user、IP、tenant、API key、device。只按 IP 会误伤共享网络或被代理绕过。

返回 429 和合理 Retry-After。

## Session

Redis 共享 Session 支持多实例。考虑 TTL、Logout、全设备退出、序列化版本、角色变化、Redis 故障和 Eviction。Session 不是普通可丢缓存。

## 验证码

短 TTL、尝试次数、一次性、避免日志泄露和账号枚举。

## 计数

Redis 原子计数适合临时指标/排行；财务事实仍需持久化与对账。

## 幂等 Key

`SET key value NX EX` 可做首次标记，但要考虑处理超过 TTL、进程崩溃、Redis 丢数据和 DB 提交顺序。订单/支付最终由 DB Unique 和业务记录兜底。

## 分布式锁

`SET NX PX` 需要唯一 owner，释放时校验。风险：TTL 到期任务仍运行、网络分区、主从切换、进程停顿、缺少 Fencing Token。

如果竞争的是同一 PostgreSQL 数据，优先行锁、Unique、条件 UPDATE、乐观锁。

锁只限制同时执行，不等于幂等，也不能回滚外部副作用。
