#!/usr/bin/env bash
set -euo pipefail
mkdir -p backups
STAMP=$(date -u +%Y%m%dT%H%M%SZ)
docker compose exec -T postgres pg_dump -U "${POSTGRES_USER:-commerce_app}" -d "${POSTGRES_DB:-commerce}" -Fc >"backups/commerce-$STAMP.dump"
echo "created backups/commerce-$STAMP.dump；必须另行执行 restore-test 才能证明可恢复。"
