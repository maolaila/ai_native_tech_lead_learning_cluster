# 公司 MCP 能力分层设计

> **所属模块：** 13 AI Engineering
> **本文用途：** 为知识、数据库、测试、CI 和可观测性设计第一版实用能力。
> **前置知识：** Tool 设计
> **建议投入：** 阅读 5 小时，设计 8 小时

---

## 1. Knowledge Server

```text
get_architecture(module?)
get_domain_rules(domain)
get_module_map()
get_coding_rules(scope)
get_api_contract(api)
search_company_docs(query, filters)
get_runbook(service, incidentType)
```

返回 source path、commit/revision、Owner、lastReviewed；检索片段而不是全部文档。

## 2. Database Read-only Server

```text
get_database_schema(environment, schema?)
get_table_definition(table)
get_index_info(table)
get_constraint_info(table)
explain_readonly_query(sql, params, environment)
check_migration(migrationDiff)
get_db_health_summary(environment)
```

严格 SQL Parser/Allowlist、只读账号、Statement Timeout、Row Limit、禁止生产任意 SQL。生产 Explain 也可能执行风险，默认使用 `EXPLAIN` 不带 `ANALYZE` 或在受控副本。

## 3. Testing Server

```text
list_test_suites()
run_test_suite(name, ref, options)
get_test_report(runId)
get_coverage(runId)
get_flaky_tests(window)
run_regression_case(caseId)
```

限制并发/时长；返回 Commit、环境、命令、状态、报告 Artifact，而不是只“passed”。

## 4. CI/CD Server

```text
get_pipeline_status(ref)
get_failed_job(runId)
get_build_artifact(runId)
get_deployment_status(environment)
get_release_diff(from,to)
running_deployments()
```

第一版只读。重新运行非生产 Job 可审批；生产部署不直接给 Agent。

## 5. Observability Server

```text
query_logs(service, timeRange, structuredFilters)
get_service_health(service, environment)
get_error_rate(route, window)
get_latency_percentiles(route, window)
get_trace(traceId)
get_recent_deployments(service)
```

时间范围、结果上限、PII 脱敏；生产只读；查询本身有成本限制。

## 6. Code/Repo

通用 Git/文件操作若 Host 已有，不重复 MCP。公司特有可做：

```text
validate_architecture_rules(diff)
get_codeowners(path)
get_related_incidents(symbol)
get_golden_example(featureType)
```

## 7. Staging Operations

后续可加入：创建 Preview Environment、Seed 测试数据、运行 Smoke。必须租户隔离、配额、自动销毁和审计。

## 8. 不暴露

任意 Shell、生产 DB 写、删除资源、IAM 管理、关闭审计、读取全部 Secret、绕过 CI、无审批生产 Deploy/Migration。
