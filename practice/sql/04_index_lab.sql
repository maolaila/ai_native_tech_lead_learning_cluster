\set ON_ERROR_STOP on
\timing on

-- Choose a user with many generated orders.
SELECT user_id, count(*)
FROM orders
GROUP BY user_id
ORDER BY count(*) DESC
LIMIT 5;

-- Baseline query. If ix_orders_user_created already exists, drop it in a
-- disposable local database to compare plans.
EXPLAIN (ANALYZE, BUFFERS)
SELECT id, order_number, status, total_amount, created_at
FROM orders
WHERE user_id = 42
ORDER BY created_at DESC, id DESC
LIMIT 20;

-- Compare a less useful single-column index.
CREATE INDEX IF NOT EXISTS ix_orders_user_only ON orders(user_id);
ANALYZE orders;

EXPLAIN (ANALYZE, BUFFERS)
SELECT id, order_number, status, total_amount, created_at
FROM orders
WHERE user_id = 42
ORDER BY created_at DESC, id DESC
LIMIT 20;

-- Correct composite index for filter + order.
CREATE INDEX IF NOT EXISTS ix_orders_user_created_lab
ON orders(user_id, created_at DESC, id DESC)
INCLUDE(status, total_amount, order_number);
ANALYZE orders;

EXPLAIN (ANALYZE, BUFFERS)
SELECT id, order_number, status, total_amount, created_at
FROM orders
WHERE user_id = 42
ORDER BY created_at DESC, id DESC
LIMIT 20;

-- Low-cardinality status experiment.
EXPLAIN (ANALYZE, BUFFERS)
SELECT count(*) FROM orders WHERE status = 'PAID';

CREATE INDEX IF NOT EXISTS ix_orders_pending_partial
ON orders(created_at)
WHERE status = 'PENDING_PAYMENT';

EXPLAIN (ANALYZE, BUFFERS)
SELECT id, created_at
FROM orders
WHERE status = 'PENDING_PAYMENT'
ORDER BY created_at
LIMIT 100;

SELECT indexname, indexdef
FROM pg_indexes
WHERE tablename='orders'
ORDER BY indexname;
