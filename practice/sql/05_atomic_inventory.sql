\set ON_ERROR_STOP on

-- Reset a selected product to one unit.
UPDATE inventory SET stock=1, version=0 WHERE product_id=1;

-- Safe atomic decrement. Exactly one concurrent transaction can affect a row
-- when stock is one and quantity is one.
UPDATE inventory
SET stock=stock-1,
    version=version+1,
    updated_at=now()
WHERE product_id=1
  AND stock>=1
RETURNING product_id, stock, version;

-- Run again: zero rows means insufficient stock.
UPDATE inventory
SET stock=stock-1,
    version=version+1,
    updated_at=now()
WHERE product_id=1
  AND stock>=1
RETURNING product_id, stock, version;

SELECT * FROM inventory WHERE product_id=1;

-- Optimistic locking shape:
-- UPDATE inventory
-- SET stock=:newStock, version=version+1
-- WHERE product_id=:id AND version=:observedVersion;
