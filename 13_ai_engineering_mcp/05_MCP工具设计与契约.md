# MCP Tool 设计与契约

> **所属模块：** 13 AI Engineering
> **本文用途：** 设计小而明确、幂等、可审计、低破坏性的工具，并给 Agent 足够的错误语义。
> **前置知识：** MCP 概念、API 设计
> **建议投入：** 阅读 6 小时，设计 8 小时

---

## 一、Tool 名称和描述

坏：`execute`、`query`、`manage_project`。

好：

```text
get_database_schema
explain_readonly_query
run_test_suite
get_pipeline_failure
query_logs
create_feature_branch
```

Description 包含用途、输入、环境、只读/写、限制和何时不要使用。

## 二、小 Tool 优于万能 Shell

`run_any_command(command)` 破坏边界、难审计、易 Prompt Injection。优先参数化 Tool，把危险选项从 Schema 中移除。

## 三、输入 Schema

```json
{
  "environment":"staging",
  "service":"commerce-api",
  "from":"2026-08-29T00:00:00Z",
  "to":"2026-08-29T01:00:00Z",
  "filters":{"traceId":"..."},
  "limit":200
}
```

枚举、长度、格式、最大时间范围、默认和互斥条件必须明确。Server 端再次校验，不能信任模型。

## 四、输出 Schema

```json
{
  "status":"ok",
  "data":[],
  "truncated":false,
  "nextCursor":null,
  "source":"log-cluster-a",
  "observedAt":"..."
}
```

结构化输出优于长自然语言。提供分页、截断和来源。

## 五、只读和幂等

同输入重复调用是否安全？

- `get_schema`：只读；
- `run_tests`：通常可重复但消耗资源；
- `create_branch`：需幂等处理；
- `deploy`：高风险，默认不暴露或强审批。

## 六、Dry Run

Migration/Backfill 等变更类能力先返回计划、影响、SQL、锁风险、预计行数、权限需求和回滚，再由审批系统执行。

## 七、错误

```text
INVALID_ARGUMENT
PERMISSION_DENIED
NOT_FOUND
CONFLICT
DEPENDENCY_UNAVAILABLE
RATE_LIMITED
TIMEOUT
PARTIAL_FAILURE
```

不要所有异常返回一段 Stack Trace；Server 内记录 traceId，客户端得到可操作错误。

## 八、超时和配额

每 Tool 设置最大时间、结果大小、调用速率、并发和资源配额。防止 Agent 无限循环跑全量 E2E/日志查询。

## 九、审计

记录 actor/user/session、tool、arguments 摘要、环境、权限、审批、结果、duration、affected resource、traceId。敏感参数脱敏。

## 十、Tool Contract 测试

Schema validation、正常、边界、无权限、超时、依赖失败、重复、并发、Output Size、Prompt Injection 输入、审计完整性。
