#!/usr/bin/env bash
set -euo pipefail
DUMP=${1:?usage: restore-test.sh backups/file.dump}
docker compose exec -T postgres createdb -U "${POSTGRES_USER:-commerce_app}" commerce_restore_test || true
cat "$DUMP" | docker compose exec -T postgres pg_restore -U "${POSTGRES_USER:-commerce_app}" -d commerce_restore_test --clean --if-exists
COUNT=$(docker compose exec -T postgres psql -U "${POSTGRES_USER:-commerce_app}" -d commerce_restore_test -Atc 'select count(*) from orders')
echo "restore verified, orders=$COUNT"
