# MCP Tool Spec：<tool_name>

## Purpose

工具解决什么公司特有问题？为什么不用现有 CLI/Resource？

## Risk Classification

Read-only / Write；Local/Staging/Production；Severity；Human Approval。

## Input Schema

```json
{}
```

枚举、格式、范围、默认、最大时间/行数/结果大小。

## Output Schema

```json
{
  "status":"ok",
  "data":{},
  "source":"",
  "observedAt":"",
  "truncated":false
}
```

## Error Contract

INVALID_ARGUMENT / PERMISSION_DENIED / NOT_FOUND / CONFLICT / TIMEOUT / DEPENDENCY_UNAVAILABLE / PARTIAL_FAILURE。

## Authorization

Actor、Role、Environment、Tenant、Resource、Approval。

## Safety Controls

Validation、Allowlist、Sandbox、Read-only Account、Rate Limit、Timeout、Redaction、Dry Run、Kill Switch。

## Idempotency / Concurrency

## Audit Fields

## Dependencies / SLO

## Test Cases

正常、边界、无权限、超时、重复、并发、Prompt Injection、结果截断、审计。

## Versioning / Compatibility

## Owner / Runbook / Deprecation
