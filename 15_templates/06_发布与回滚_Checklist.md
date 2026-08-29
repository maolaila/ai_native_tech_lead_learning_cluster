# Release & Rollback Checklist

## Before

- [ ] Scope/Owner/Communication；
- [ ] CI、Security、Contract、Migration 通过；
- [ ] Artifact Digest；
- [ ] Feature Flag；
- [ ] Capacity；
- [ ] Dashboard/Alert/Runbook；
- [ ] DB 备份/恢复点（按风险）；
- [ ] 回滚 Artifact 存在；
- [ ] 新旧兼容；
- [ ] 停止条件。

## Deploy

- [ ] Staging 同 Digest；
- [ ] Migration 独立执行；
- [ ] Readiness；
- [ ] Smoke；
- [ ] Canary 1/5/25/100%；
- [ ] Error/Latency/Business；
- [ ] Queue/Outbox/DB Pool；
- [ ] 审批记录。

## Stop Conditions

5xx、P99、SLO Burn、订单成功、数据不变量、DLQ、资源、外部依赖。

## Rollback

- Target Digest:
- DB Compatibility:
- Flag Action:
- Consumer/Job Action:
- Data Repair:
- Verification:
- Communication:

## After

- [ ] 观察窗口；
- [ ] 清理旧任务/Flag；
- [ ] 发布记录；
- [ ] 问题进入 Incident/Regression/Rule。
