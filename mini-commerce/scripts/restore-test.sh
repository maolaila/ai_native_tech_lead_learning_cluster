#!/usr/bin/env bash
# 作用：把备份恢复到本次新建的临时数据库，验证后删除临时库，不覆盖原业务库。
# 为什么：备份文件存在不等于能恢复；不能用固定库名配合 --clean 清空已有数据。
# 对应文档：mini-commerce/docs/LEARNING-READINESS.md；仅供本地 Compose 学习环境。
set -euo pipefail
DUMP=${1:?用法：bash scripts/restore-test.sh backups/file.dump}
if [[ ! -f "$DUMP" || ! -r "$DUMP" || ! -s "$DUMP" ]]; then
  printf '备份文件不存在、不可读或为空：%s\n' "$DUMP" >&2
  exit 1
fi
# 先把调用者传入的相对路径转成绝对路径，再切换到 Compose 目录。
DUMP="$(cd "$(dirname "$DUMP")" && pwd)/$(basename "$DUMP")"
cd "$(dirname "${BASH_SOURCE[0]}")/.."
RESTORE_DB="commerce_restore_$(date -u +%Y%m%d%H%M%S)_${RANDOM}_${RANDOM}"
CREATED=false
cleanup() {
  local status=$?
  if [[ "$CREATED" == true ]]; then
    if ! docker compose exec -T postgres sh -eu -c \
      'exec dropdb -U "$POSTGRES_USER" "$1"' sh "$RESTORE_DB"; then
      printf '本次临时库清理失败，请检查：%s\n' "$RESTORE_DB" >&2
      status=1
    fi
  fi
  exit "$status"
}
trap cleanup EXIT
# 只有成功创建的随机临时库，才允许 cleanup 删除。创建失败时不会删除任何旧库。
docker compose exec -T postgres sh -eu -c \
  'exec createdb -U "$POSTGRES_USER" "$1"' sh "$RESTORE_DB"
CREATED=true
# 新库不需要 --clean；任意恢复错误都停止，不把部分恢复标记为成功。
docker compose exec -T postgres sh -eu -c \
  'exec pg_restore --exit-on-error -U "$POSTGRES_USER" -d "$1"' sh "$RESTORE_DB" < "$DUMP"
COUNT=$(docker compose exec -T postgres sh -eu -c \
  'exec psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$1" -Atc "select count(*) from orders"' sh "$RESTORE_DB")
printf '恢复及订单查询成功：orders=%s；原业务库未被覆盖。\n' "$COUNT"
# EXIT 会清理本次临时库。此演练不等于已验证全部灾备策略或跨版本恢复。
