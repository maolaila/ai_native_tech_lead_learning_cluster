# PostgreSQL 死锁实验

会话 A：`BEGIN; UPDATE inventory SET available=available WHERE product_id=1;`，再等待。

会话 B：`BEGIN; UPDATE inventory SET available=available WHERE product_id=2;`，再执行 product_id=1。

回到 A 更新 product_id=2。PostgreSQL 会中止一个事务。观察 `pg_stat_activity` 和日志。

修复原则：多商品按 product_id 固定顺序锁定，缩短事务；应用只对可恢复错误有限重试，并重试整个事务。
