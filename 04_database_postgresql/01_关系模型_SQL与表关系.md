# 关系模型、SQL 与表关系

> **所属模块：** 04 Database
> **本文用途：** 理解表怎样表达业务事实，并掌握日常业务查询。
> **前置知识：** 基础 SQL
> **建议投入：** 阅读 4 小时，SQL 练习 6 小时

---

## 一、表表达事实

```text
users：用户事实
products：商品事实
orders：订单事实
order_items：订单包含哪些商品的事实
```

数据库不只是存储，它还提供约束、并发、事务、查询计划和恢复。

## 二、主键

```sql
CREATE TABLE users (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  email text NOT NULL
);
```

自增 ID 紧凑、易读；UUID 可在应用生成、跨系统唯一，但更大且顺序性取决于类型。选择要有理由。

## 三、外键

```sql
CREATE TABLE orders (
  id bigint PRIMARY KEY,
  user_id bigint NOT NULL REFERENCES users(id)
);
```

保证订单引用的用户存在。初学项目优先使用外键，让数据库保护完整性。

## 四、关系

一对多：User 1 → N Order；Order 1 → N OrderItem。

多对多使用关联表：

```sql
CREATE TABLE product_categories (
  product_id bigint REFERENCES products(id),
  category_id bigint REFERENCES categories(id),
  PRIMARY KEY(product_id, category_id)
);
```

不要把 ID 列表存成 `"1,2,3"`，否则难外键、索引、查询、去重和更新。

## 五、CRUD

```sql
INSERT INTO products(name, price, status)
VALUES ('Keyboard', 1200, 'PUBLISHED')
RETURNING id;

SELECT id, name, price
FROM products
WHERE status='PUBLISHED'
ORDER BY created_at DESC
LIMIT 20;

UPDATE products SET price=1300 WHERE id=42;
DELETE FROM cart_items WHERE cart_id=10 AND product_id=42;
```

生产查询避免无脑 `SELECT *`：契约不清、读取无关列、传输增加、表变化影响结果。

## 六、JOIN

INNER JOIN 只返回匹配；LEFT JOIN 保留左表。

```sql
SELECT o.id, u.email
FROM orders o
JOIN users u ON u.id=o.user_id;
```

一对多 JOIN 后主表会重复。在订单主表上直接 JOIN Item 再分页，可能得到错误页。先明确是查明细、聚合还是主表分页。

## 七、聚合

```sql
SELECT status, count(*)
FROM orders
GROUP BY status;
```

`WHERE` 在聚合前过滤，`HAVING` 在聚合后过滤。

## 八、CTE / Subquery

用来表达复杂步骤，但不要为“高级”把简单查询写成多层嵌套。可读性和执行计划都要看。

## 九、NULL

`NULL` 不是空字符串或 0：

```sql
WHERE cancelled_at IS NULL
```

尽量通过 `NOT NULL` 减少无意义的三值逻辑。

## 十、金额与时间

- 金额使用 `numeric` 或最小货币单位整数；
- 明确 Currency 和舍入；
- 时间不要全部存字符串；
- 区分 Instant、Date、业务时区。

## 十一、练习查询

用户最近订单、订单详情、销量 Top10、30 天状态统计、从未下单用户、低库存、过期未用券、累计消费、支付成功但订单未 Paid 的一致性检查。
