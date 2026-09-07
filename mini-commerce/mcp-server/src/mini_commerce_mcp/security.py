"""工具边界与脱敏：这些检查不是操作系统沙箱，也不替代数据库最小权限。"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

SECRET_KEY = re.compile(r"(?i)(password|token|secret|api[_-]?key|authorization|cookie)")
SECRET_ASSIGNMENT = re.compile(
    r"""(?i)\b([\w-]*(?:password|token|secret|api[_-]?key)[\w-]*)["']?\s*[:=]\s*["']?[^"'\s,;}]+"""
)
ACCESS_KEY = re.compile(r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b")
PROMPT_INJECTION = re.compile(
    r"(?i)(ignore (all|previous) instructions|忽略.{0,10}(指令|规则)|send.{0,20}secret|泄露.{0,10}(密钥|凭证))"
)


def safe_resolve(root: Path, relative: str) -> Path:
    """先解析 .. 和符号链接，再检查文件确实仍在仓库中。"""
    candidate = (root / relative).resolve()
    try:
        candidate.relative_to(root.resolve())
    except ValueError as exc:
        raise ValueError("PERMISSION_DENIED: path escapes repository root") from exc
    return candidate


def validate_readonly_sql(sql: str) -> str:
    """只接受一条 SELECT/WITH；工具自己添加 EXPLAIN，不接受用户自带 EXPLAIN。"""
    normalized = " ".join(sql.strip().split()).rstrip(";")
    if not normalized or len(normalized) > 5000:
        raise ValueError("INVALID_ARGUMENT: SQL length must be 1..5000")
    if ";" in normalized or "--" in normalized or "/*" in normalized:
        raise ValueError(
            "INVALID_ARGUMENT: comments and multiple statements are not supported"
        )
    if not re.match(r"(?i)^(select|with)\s", normalized):
        raise ValueError(
            "PERMISSION_DENIED: supply SELECT/WITH, not EXPLAIN or a write"
        )
    if re.search(
        r"(?i)\b(insert|update|delete|alter|drop|truncate|grant|revoke|copy|call|do|create|analyze|into)\b",
        normalized,
    ):
        raise ValueError("PERMISSION_DENIED: write or execution keyword")
    return normalized


def redact(value: Any) -> Any:
    """先按结构处理敏感字段；不要对序列化后的 JSON 替换再反序列化。"""
    if isinstance(value, dict):
        return {
            str(key): "<redacted>" if SECRET_KEY.search(str(key)) else redact(item)
            for key, item in value.items()
        }
    if isinstance(value, (list, tuple)):
        return [redact(item) for item in value]
    if isinstance(value, str):
        result = SECRET_ASSIGNMENT.sub(
            lambda match: match.group(1) + "=<redacted>", value
        )
        result = ACCESS_KEY.sub("<redacted-access-key>", result)
        result = re.sub(r"(?i)\bBearer\s+[\w.\-]+", "Bearer <redacted>", result)
        return re.sub(r"(\w+://)[^\s/:@]+:[^\s/@]+@", r"\1<redacted>@", result)
    if value is None or isinstance(value, (bool, int, float)):
        return value
    return redact(str(value))


def untrusted_excerpt(text: str) -> dict[str, Any]:
    """检索结果只是资料；提示注入检测只能提供信号，不能证明文档安全。"""
    return {
        "trust": "untrusted_document_data",
        "promptInjectionSuspected": bool(PROMPT_INJECTION.search(text)),
        "text": redact(text[:2000]),
    }
