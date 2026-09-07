#!/usr/bin/env bash
# 作用：备份当前本地 Compose 的业务库；仅供学习环境使用。
# 为什么：先写临时文件，pg_dump 成功才改成 .dump，避免把半份文件误当作备份。
# 对应文档：04_database_postgresql/07_连接池_Migration与备份.md、mini-commerce/docs/LEARNING-READINESS.md。
set -euo pipefail
umask 077
cd "$(dirname "${BASH_SOURCE[0]}")/.."
mkdir -p backups
TEMP=$(mktemp "backups/commerce-$(date -u +%Y%m%dT%H%M%SZ)-XXXXXX.partial")
trap 'rm -f "$TEMP"' EXIT
# 在容器内部取账号和库名，才能与 Compose 解析后的 .env 保持一致。
docker compose exec -T postgres sh -eu -c \
  'exec pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" -Fc' > "$TEMP"
test -s "$TEMP"
DUMP="${TEMP%.partial}.dump"
mv "$TEMP" "$DUMP"
printf '备份文件已生成；还需要恢复演练，不能只检查文件存在。\n' >&2
# stdout 只输出路径，便于下一条命令接收；不输出密码或业务内容。
printf '%s/%s\n' "$PWD" "$DUMP"
