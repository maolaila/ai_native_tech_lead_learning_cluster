-- 先保存无索引计划，再创建与“用户最近订单”查询形状一致的复合索引并比较。
EXPLAIN (ANALYZE,BUFFERS) SELECT id,status,total_amount FROM orders WHERE user_id=(SELECT min(id) FROM app_users) ORDER BY created_at DESC,id DESC LIMIT 20;
-- 生产 CREATE INDEX 需评估锁；大表通常另行使用 CONCURRENTLY，且不能放普通事务型 Migration。
CREATE INDEX IF NOT EXISTS lab_orders_user_created ON orders(user_id,created_at DESC,id DESC);
EXPLAIN (ANALYZE,BUFFERS) SELECT id,status,total_amount FROM orders WHERE user_id=(SELECT min(id) FROM app_users) ORDER BY created_at DESC,id DESC LIMIT 20;
