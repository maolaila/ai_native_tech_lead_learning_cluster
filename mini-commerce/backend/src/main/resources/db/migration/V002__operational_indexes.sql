-- 对应文档：04_database_postgresql/03_索引与EXPLAIN.md。
-- 索引必须服务真实查询形状；不是“每列都建索引”。
create index if not exists ix_idempotency_expiry on idempotency_records(expires_at);
create index if not exists ix_refresh_expiry on refresh_tokens(expires_at) where revoked_at is null;
create index if not exists ix_payment_order_created on payment_attempts(order_id,created_at desc);
