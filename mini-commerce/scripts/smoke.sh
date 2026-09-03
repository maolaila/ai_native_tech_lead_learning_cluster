#!/usr/bin/env bash
set -euo pipefail
BASE=${BASE_URL:-http://localhost:18080}
TMP=$(mktemp);trap 'rm -f "$TMP"' EXIT
curl -fsS "$BASE/actuator/health/readiness"
curl -fsS -H 'Content-Type: application/json' -d '{"email":"alice@example.com","password":"Password123!"}' "$BASE/api/auth/login" >"$TMP"
TOKEN=$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))["accessToken"])' "$TMP")
curl -fsS "$BASE/api/products"
curl -fsS -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' -H "Idempotency-Key: smoke-$(date +%s)" -d '{"items":[{"productId":1,"quantity":1}]}' "$BASE/api/orders"
echo 'smoke passed'
