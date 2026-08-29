# 索引、B-Tree、复合索引与 EXPLAIN

> **所属模块：** 04 Database
> **本文用途：** 理解索引为什么加速、为什么增加写成本，并用执行计划验证。
> **前置知识：** SQL 与 Schema
> **建议投入：** 阅读 5 小时，百万数据实验 8 小时

---

## 一、没有索引

```sql
SELECT id,status,total_amount
FROM orders
WHERE user_id=42;
```

可能扫描 100 万行逐一判断。B-Tree 索引维护有序键，能快速缩小候选范围。

## 二、代价

每次 INSERT、UPDATE 索引列、DELETE 都要维护索引；占磁盘和缓存；增加 Vacuum、Migration 和优化器成本。不是越多越好。

## 三、单列和复合

```sql
CREATE INDEX ix_orders_user ON orders(user_id);
```

若真实查询：

```sql
WHERE user_id=?
ORDER BY created_at DESC
LIMIT 20
```

可能更适合：

```sql
CREATE INDEX ix_orders_user_created
ON orders(user_id, created_at DESC);
```

复合顺序像“姓→名→生日”的电话簿。是否有效必须看执行计划，不机械背口诀。

## 四、选择性

Status 只有四种值，单列索引可能价值低。若只有少量 Pending，可用 Partial Index：

```sql
CREATE INDEX ix_orders_pending
ON orders(created_at)
WHERE status='PENDING_PAYMENT';
```

## 五、表达式索引

查询 `lower(email)`，普通 email 索引未必匹配：

```sql
CREATE UNIQUE INDEX ux_users_lower_email
ON users(lower(email));
```

## 六、覆盖

```sql
CREATE INDEX ix_orders_user_created
ON orders(user_id, created_at DESC)
INCLUDE(status,total_amount);
```

可能支持 Index Only Scan，但索引更大。只为真实高频查询使用。

## 七、EXPLAIN

```sql
EXPLAIN SELECT ...;
EXPLAIN (ANALYZE, BUFFERS) SELECT ...;
```

观察 Seq/Index Scan、Estimated/Actual Rows、Loops、Sort、Buffers、Planning/Execution Time。

`ANALYZE` 会真实执行语句，对 UPDATE/DELETE 非常危险。

## 八、不是“走索引就一定好”

小表或返回比例很高时 Seq Scan 可能更便宜。重点看扫描量、返回量、估计准确、排序、Loop 和总耗时。

## 九、N+1

1 次查 100 订单，再 100 次查用户。每条 SQL 都快，总请求仍慢。需 JOIN、Batch、Fetch 或查询模型，而不是只加索引。

## 十、生产建索引

普通建索引可能阻塞写；`CREATE INDEX CONCURRENTLY` 减少阻塞但更慢、有失败处理和事务限制。Migration 要有专门策略。

## 十一、实验

生成 100 万订单，比较无索引、单列、复合、错误顺序、Partial；保存 `EXPLAIN (ANALYZE, BUFFERS)` 和索引大小、写入影响。
