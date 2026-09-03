from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
PROJECT = REPO / "mini-commerce"


def write(relative: str, content: str) -> None:
    path = REPO / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


write("mini-commerce/mcp-server/Dockerfile", r'''FROM python:3.13-slim
RUN useradd --system --uid 10001 app \
    && mkdir -p /app /audit \
    && chown -R app:app /app /audit
WORKDIR /app
COPY pyproject.toml ./
COPY src src
RUN pip install --no-cache-dir .
USER 10001
EXPOSE 8081
ENTRYPOINT ["mini-commerce-mcp"]
''')

write("mini-commerce/mcp-server/.dockerignore", r'''__pycache__
.pytest_cache
.venv
*.egg-info
build
dist
*.log
''')

# 命名卷首次挂载会以镜像中 /audit 的目录元数据初始化，因此非 root 进程能够写审计 JSONL。
compose = PROJECT / "compose.yaml"
text = compose.read_text(encoding="utf-8")
text = text.replace(
    "      - mcp-audit:/audit\n    depends_on:",
    "      - mcp-audit:/audit\n    depends_on:",
)
compose.write_text(text, encoding="utf-8")

# 将本补丁加入一键重建入口。
regenerator = REPO / "tools/regenerate_complete_project.py"
if regenerator.exists():
    text = regenerator.read_text(encoding="utf-8")
    needle = '    "tools/apply_release_cleanup_v7.py",\n'
    replacement = needle + '    "tools/apply_final_runtime_fix_v8.py",\n'
    if replacement not in text:
        text = text.replace(needle, replacement)
    regenerator.write_text(text, encoding="utf-8")

print(json.dumps({"status": "final-runtime-fix-v8-applied"}, ensure_ascii=False))
