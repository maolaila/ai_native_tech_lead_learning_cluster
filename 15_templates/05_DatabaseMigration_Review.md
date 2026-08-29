# Database Migration Review

- Migration ID:
- Owner:
- Target Environment:
- Tables / Estimated Rows / Size:

## Change

SQL/Diff、业务目的、应用版本依赖。

## Compatibility

- [ ] 旧应用兼容新 Schema；
- [ ] 新应用兼容旧/过渡 Schema；
- [ ] 滚动发布期间双版本；
- [ ] Event/API 兼容。

## Lock / Performance

锁级别、预计时长、全表扫描、重写表、索引方式、WAL/Replica Lag、Statement/Lock Timeout。

## Data Backfill

批大小、顺序、限速、断点、幂等、校验、停止条件。

## Constraints

是否先 `NOT VALID`、何时验证、Null/Default、Unique 冲突处理。

## Rollout

Expand→Deploy→Backfill→Switch→Observe→Contract。

## Rollback / Forward Fix

应用回滚兼容？数据可逆？需要备份？

## Monitoring

DB Lock、Query Latency、CPU/IO、Replication、Error、Business Invariant。

## Dry Run / Staging Evidence

## Approval

DB Owner / Tech Lead / Operations / Security（按风险）。
