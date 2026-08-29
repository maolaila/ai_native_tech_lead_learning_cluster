# PostgreSQL 双会话死锁实验

仅在本地实验库执行。

## 准备

```sql
UPDATE inventory SET stock=10 WHERE product_id IN (1,2);
```

## Session A

```sql
BEGIN;
SELECT * FROM inventory WHERE product_id=1 FOR UPDATE;
-- 保持事务不提交
```

## Session B

```sql
BEGIN;
SELECT * FROM inventory WHERE product_id=2 FOR UPDATE;
```

## Session A

```sql
SELECT * FROM inventory WHERE product_id=2 FOR UPDATE;
-- 等待 B
```

## Session B

```sql
SELECT * FROM inventory WHERE product_id=1 FOR UPDATE;
-- PostgreSQL 检测环，终止其中一个事务
```

## 观察

第三个 Session：

```sql
SELECT pid, state, wait_event_type, wait_event, query
FROM pg_stat_activity
WHERE datname=current_database();
```

## 修复

所有订单按 `product_id ASC` 锁定：

```sql
SELECT *
FROM inventory
WHERE product_id = ANY(:ids)
ORDER BY product_id
FOR UPDATE;
```

应用仍需对 Deadlock/Serialization Failure 做有限的“整个事务”重试。

## 记录

死锁日志、两个 Session 时间线、被中止事务、重试次数、固定顺序后的结果。
