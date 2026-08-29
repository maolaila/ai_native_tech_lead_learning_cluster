\set ON_ERROR_STOP on

INSERT INTO users(email, display_name, role)
VALUES
  ('alice@example.com','Alice','USER'),
  ('bob@example.com','Bob','USER'),
  ('admin@example.com','Admin','ADMIN')
ON CONFLICT DO NOTHING;

INSERT INTO products(name, price, currency, status)
VALUES
  ('Mechanical Keyboard', 8000, 'JPY', 'PUBLISHED'),
  ('Wireless Mouse', 3500, 'JPY', 'PUBLISHED'),
  ('USB-C Hub', 5000, 'JPY', 'PUBLISHED')
ON CONFLICT DO NOTHING;

INSERT INTO inventory(product_id, stock)
SELECT id, CASE name
  WHEN 'Mechanical Keyboard' THEN 10
  WHEN 'Wireless Mouse' THEN 30
  ELSE 20 END
FROM products
ON CONFLICT (product_id) DO NOTHING;
