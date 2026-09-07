#!/usr/bin/env bash
set -euo pipefail
# 兼容旧入口；逻辑集中在同一份 Python 脚本。
exec python3 "$(dirname "$0")/smoke.py"
