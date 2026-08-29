# Feature Spec：<功能名>

## 1. 背景与问题

当前发生什么？用户/业务损失？为什么现在做？

## 2. 目标

可测量结果；不要写“体验更好”而无指标。

## 3. 不在范围

明确本次不做什么，防止 AI/团队自动扩展。

## 4. Actor 与场景

| Actor | 场景 | 权限 |
|---|---|---|
| | | |

## 5. 业务规则和不变量

1. 
2. 
3. 

## 6. 状态机

```text
STATE_A → STATE_B
```

合法/非法转换、触发者、副作用。

## 7. 输入输出

Request、Response、Error Code、Idempotency、Pagination、兼容。

## 8. 数据

新增/变更表、Owner、约束、索引、保留、敏感等级、Migration。

## 9. 失败与恢复

无效输入、权限、重复、并发、部分失败、依赖超时、重试、补偿。

## 10. 非功能

规模、P95/P99、Availability、一致性、RPO/RTO、安全、成本。

## 11. 验收条件

用 Given/When/Then；包含正常、边界、异常和权限。

## 12. Observability

Logs、Metrics、Traces、Business Invariant、Alert。

## 13. 发布

Flag、Migration 顺序、兼容、Canary、停止条件、回滚/前滚。

## 14. 未决问题与 Owner

| 问题 | Owner | Deadline |
|---|---|---|
