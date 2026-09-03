from __future__ import annotations
import json,re
from pathlib import Path
from typing import Any

SECRET_PATTERNS=[re.compile(r"(?i)(password|token|secret|api[_-]?key)\s*[:=]\s*([^\s,]+)"),re.compile(r"AKIA[0-9A-Z]{16}")]
PROMPT_INJECTION=re.compile(r"(?i)(ignore (all|previous) instructions|忽略.{0,10}(指令|规则)|send.{0,20}secret|泄露.{0,10}(密钥|凭证))")

def safe_resolve(root:Path,relative:str)->Path:
    """对应文档 13_ai_engineering_mcp/07：规范化后必须仍位于只读根目录。"""
    candidate=(root/relative).resolve()
    try:candidate.relative_to(root.resolve())
    except ValueError as exc:raise ValueError("PERMISSION_DENIED: path escapes repository root") from exc
    return candidate

def validate_readonly_sql(sql:str)->str:
    normalized=" ".join(sql.strip().split())
    if len(normalized)>5000:raise ValueError("INVALID_ARGUMENT: SQL too long")
    if ";" in normalized.rstrip(";"):raise ValueError("INVALID_ARGUMENT: only one statement")
    lower=normalized.lower().rstrip(";")
    if not (lower.startswith("select ") or lower.startswith("with ") or lower.startswith("explain ")):raise ValueError("PERMISSION_DENIED: read-only SQL required")
    if re.search(r"\b(insert|update|delete|alter|drop|truncate|grant|revoke|copy|call|do|create)\b",lower):raise ValueError("PERMISSION_DENIED: write or DDL keyword")
    return normalized.rstrip(";")

def redact(value:Any)->Any:
    text=json.dumps(value,ensure_ascii=False,default=str)
    for pattern in SECRET_PATTERNS:text=pattern.sub(lambda m:m.group(1)+"=<redacted>",text)
    return json.loads(text)

def untrusted_excerpt(text:str)->dict[str,Any]:
    return {"trust":"untrusted_document_data","promptInjectionSuspected":bool(PROMPT_INJECTION.search(text)),"text":text[:2000]}
