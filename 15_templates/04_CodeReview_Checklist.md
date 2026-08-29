# Code Review Checklist

## 1. Requirement

- [ ] 与 Feature Spec/Acceptance 对齐；
- [ ] 不变量和状态清楚；
- [ ] 没有未声明扩展范围。

## 2. Architecture

- [ ] 模块和 Data Owner 正确；
- [ ] 依赖方向合法；
- [ ] Controller 无核心业务；
- [ ] 无穿透内部 Repository；
- [ ] 复杂度与需求匹配。

## 3. Data

- [ ] Migration/约束/索引；
- [ ] 事务边界；
- [ ] 并发、锁、幂等；
- [ ] 金额/时间/快照；
- [ ] 兼容和恢复。

## 4. API

- [ ] DTO 白名单；
- [ ] Validation/Error；
- [ ] Status/Contract；
- [ ] Pagination/Idempotency；
- [ ] Backward Compatibility。

## 5. Security

- [ ] Authentication/Authorization/Object Ownership；
- [ ] Input/Output；
- [ ] XSS/CSRF/SQLi/SSRF；
- [ ] Secret/PII；
- [ ] Dependency/Permission。

## 6. Reliability

- [ ] Timeout/Retry/Backoff；
- [ ] Retry 写操作安全；
- [ ] MQ Ack/Idempotency/DLQ；
- [ ] Cache Failure；
- [ ] Partial Failure。

## 7. Tests

- [ ] 正常、边界、异常、权限；
- [ ] Integration 用真实依赖；
- [ ] Regression；
- [ ] 测试不迎合实现；
- [ ] 无 Flaky/Sleep。

## 8. Operations

- [ ] Logs/Metrics/Traces；
- [ ] Health；
- [ ] Config/Secret；
- [ ] Deploy/Migration/Rollback；
- [ ] Runbook。

## 9. AI Disclosure

- [ ] AI 修改范围；
- [ ] 未验证假设；
- [ ] Agent 运行了什么 Tool；
- [ ] 人确认了关键证据。
