"""本地学习工具。默认只读；运行仓库测试是执行代码，必须单独显式开启。"""

from __future__ import annotations

import functools
import json
import os
import signal
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from .security import redact, safe_resolve, untrusted_excerpt, validate_readonly_sql

ROOT = Path(os.getenv("REPOSITORY_ROOT", Path(__file__).resolve().parents[4])).resolve()
AUDIT = Path(os.getenv("MCP_AUDIT_PATH", ROOT / "mini-commerce/mcp-audit/audit.jsonl"))
SUITES = {
    "backend-unit": ["mvn", "-B", "test"],
    "backend-all": ["mvn", "-B", "verify"],
    "mcp": [sys.executable, "-m", "pytest", "-q"],
}
MAX_FILE_BYTES = 1_000_000


def audit(tool: str, args: dict[str, Any], status: str, duration_ms: int) -> None:
    AUDIT.parent.mkdir(parents=True, exist_ok=True)
    row = {
        "observedAt": datetime.now(timezone.utc).isoformat(),
        "actor": "local-learning-client",
        "tool": tool,
        "arguments": redact(args),
        "status": status,
        "durationMs": duration_ms,
    }
    with AUDIT.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(row, ensure_ascii=False) + "\n")


def audited(tool: str):
    """成功与拒绝都留痕；不把异常原文（可能包含凭证）直接写入日志。"""

    def decorate(function):
        @functools.wraps(function)
        def wrapped(*args, **kwargs):
            started = time.monotonic()
            status = "error"
            try:
                result = function(*args, **kwargs)
                status = result.get("status", "ok")
                return result
            finally:
                audit(
                    tool,
                    {"args": args, "kwargs": kwargs},
                    status,
                    int((time.monotonic() - started) * 1000),
                )

        return wrapped

    return decorate


def bounded_read(path: Path) -> str:
    with path.open("rb") as stream:
        data = stream.read(MAX_FILE_BYTES + 1)
    if len(data) > MAX_FILE_BYTES:
        raise ValueError("INVALID_ARGUMENT: document exceeds size limit")
    return data.decode("utf-8", errors="replace")


@audited("search_learning_docs")
def search_docs(query: str, limit: int = 8) -> dict[str, Any]:
    if not query.strip() or len(query) > 300:
        raise ValueError("INVALID_ARGUMENT: query length must be 1..300")
    limit = max(1, min(limit, 20))
    terms = [term.lower() for term in query.split()]
    directories = [p for p in ROOT.iterdir() if p.is_dir() and p.name[:2].isdigit()]
    directories.append(ROOT / "mini-commerce/docs")
    candidates = [ROOT / "README.md"]
    for directory in directories:
        candidates.extend(directory.rglob("*.md"))
    results = []
    for path in candidates[:2500]:
        try:
            real = safe_resolve(ROOT, str(path.relative_to(ROOT)))
            text = bounded_read(real)
        except (ValueError, OSError):
            continue
        score = sum(text.lower().count(term) for term in terms)
        if score:
            pos = min(text.lower().find(term) for term in terms if term in text.lower())
            excerpt = text[max(0, pos - 300) : pos + 1200].replace("\x00", "")
            results.append(
                (
                    score,
                    {
                        "source": str(path.relative_to(ROOT)),
                        "score": score,
                        "excerpt": untrusted_excerpt(excerpt),
                    },
                )
            )
    data = [
        item
        for _, item in sorted(results, key=lambda row: (-row[0], row[1]["source"]))[
            :limit
        ]
    ]
    return {
        "status": "ok",
        "data": data,
        "truncated": len(results) > limit or len(candidates) > 2500,
        "sourceRevision": os.getenv("GIT_COMMIT", "workspace"),
        "observedAt": datetime.now(timezone.utc).isoformat(),
    }


@audited("read_runbook")
def read_runbook(relative_path: str) -> dict[str, Any]:
    path = safe_resolve(ROOT, relative_path)
    allowed = (ROOT / "mini-commerce/docs/runbooks").resolve()
    try:
        path.relative_to(allowed)
    except ValueError as exc:
        raise ValueError("PERMISSION_DENIED: only runbooks are readable") from exc
    text = bounded_read(path)
    return {
        "status": "ok",
        "source": str(path.relative_to(ROOT)),
        "data": untrusted_excerpt(text),
        "truncated": len(text) > 2000,
    }


def connect_readonly(url: str):
    import psycopg

    return psycopg.connect(
        url,
        connect_timeout=3,
        options="-c default_transaction_read_only=on -c statement_timeout=2000 -c lock_timeout=1000",
    )


@audited("get_database_schema")
def database_schema() -> dict[str, Any]:
    url = os.getenv("DATABASE_READONLY_URL")
    if not url:
        folder = safe_resolve(
            ROOT, "mini-commerce/backend/src/main/resources/db/migration"
        )
        files = sorted(folder.glob("V*.sql"))
        migrations = [
            {
                "source": str(path.relative_to(ROOT)),
                "ddl": bounded_read(safe_resolve(ROOT, str(path.relative_to(ROOT)))),
            }
            for path in files
        ]
        result = {
            "mode": "migration-history",
            "migrations": migrations,
            "note": "这是有序迁移历史，不是已经连接数据库验证的最终 Schema。",
        }
        truncated = False
    else:
        with connect_readonly(url) as connection:
            rows = connection.execute(
                "select table_name,column_name,data_type,is_nullable from information_schema.columns where table_schema='public' order by table_name,ordinal_position limit 2001"
            ).fetchall()
        result = {
            "mode": "live-readonly",
            "columns": [
                {"table": r[0], "column": r[1], "type": r[2], "nullable": r[3]}
                for r in rows[:2000]
            ],
        }
        truncated = len(rows) > 2000
    return {"status": "ok", "data": result, "truncated": truncated}


@audited("explain_readonly_query")
def explain_readonly(sql: str) -> dict[str, Any]:
    safe = validate_readonly_sql(sql)
    url = os.getenv("DATABASE_READONLY_URL")
    if not url:
        raise RuntimeError(
            "DEPENDENCY_UNAVAILABLE: DATABASE_READONLY_URL is not configured"
        )
    with connect_readonly(url) as connection:
        plan = connection.execute("EXPLAIN (FORMAT JSON) " + safe).fetchone()[0]
    return {
        "status": "ok",
        "data": redact(plan),
        "analyze": False,
        "note": "不执行 EXPLAIN ANALYZE；仍需真正的只读数据库角色，SQL 关键词检查不是安全沙箱。",
    }


def execution_enabled() -> bool:
    return (
        os.getenv("MCP_ENABLE_TEST_EXECUTION") == "true"
        and os.getenv("MCP_TRANSPORT", "stdio") == "stdio"
        and os.name == "posix"
    )


@audited("run_test_suite")
def run_suite(name: str) -> dict[str, Any]:
    if name not in SUITES:
        raise ValueError("INVALID_ARGUMENT: suite is not allowlisted")
    if not execution_enabled():
        raise ValueError(
            "PERMISSION_DENIED: code execution disabled; trusted local stdio opt-in required"
        )
    cwd = safe_resolve(
        ROOT, "mini-commerce/" + ("mcp-server" if name == "mcp" else "backend")
    )
    # 固定命令仍会执行仓库中的任意测试代码，不能称为只读工具或完整沙箱。
    environment = {
        key: os.environ[key]
        for key in ("PATH", "HOME", "JAVA_HOME", "LANG")
        if key in os.environ
    }
    with tempfile.TemporaryFile() as output:
        process = subprocess.Popen(
            SUITES[name],
            cwd=cwd,
            stdout=output,
            stderr=subprocess.STDOUT,
            env=environment,
            shell=False,
            start_new_session=True,
        )
        try:
            exit_code = process.wait(timeout=600)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL)
            process.wait()
            raise RuntimeError("TIMEOUT: test process group terminated") from None
        size = output.tell()
        output.seek(max(0, size - 20000))
        text = output.read().decode("utf-8", errors="replace")
    return {
        "status": "passed" if exit_code == 0 else "failed",
        "exitCode": exit_code,
        "command": SUITES[name],
        "output": redact(text),
        "truncated": size > 20000,
    }
