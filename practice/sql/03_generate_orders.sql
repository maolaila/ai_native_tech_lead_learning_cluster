\set ON_ERROR_STOP on
\if :{?order_count}
\else
  \set order_count 100000
\endif

-- Add synthetic users first.
INSERT INTO users(email, display_name, role)
SELECT 'load-user-' || g || '@example.com', 'Load User ' || g, 'USER'
FROM generate_series(1, 10000) g
ON CONFLICT DO NOTHING;

-- Disable the user-created index during the first experiment if you want to
-- observe an unindexed query. Keep the UNIQUE order_number constraint.
INSERT INTO orders(order_number, user_id, status, total_amount, currency, created_at, updated_at)
SELECT
  'LOAD-' || lpad(g::text, 12, '0'),
  1 + (g % 10000),
  (ARRAY['PENDING_PAYMENT','PAID','CANCELLED','COMPLETED'])[1 + (g % 4)],
  1000 + (g % 50000),
  'JPY',
  now() - ((g % 365) || ' days')::interval - ((g % 86400) || ' seconds')::interval,
  now()
FROM generate_series(1, :order_count) g
ON CONFLICT (order_number) DO NOTHING;

ANALYZE users;
ANALYZE orders;

SELECT count(*) AS order_count FROM orders;
