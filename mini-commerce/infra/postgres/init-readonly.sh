#!/usr/bin/env bash
set -euo pipefail
# 仅新建的本地演示数据库执行。只读是数据库权限，不是变量名或客户端自律。
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" \
  -v db="$POSTGRES_DB" -v app_user="$POSTGRES_USER" \
  -v readonly_password="${MCP_DATABASE_PASSWORD:-commerce-readonly-local}" <<'SQL'
CREATE ROLE commerce_readonly LOGIN PASSWORD :'readonly_password';
GRANT CONNECT ON DATABASE :"db" TO commerce_readonly;
GRANT USAGE ON SCHEMA public TO commerce_readonly;
ALTER ROLE commerce_readonly SET default_transaction_read_only = on;
SQL
