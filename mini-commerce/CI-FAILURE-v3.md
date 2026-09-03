# CI 失败报告（main 未更新）

- Workflow: https://github.com/maolaila/ai_native_tech_lead_learning_cluster/actions/runs/33722176519
- Commit: f9caf572ec0c43ff3029eae76e9301484221f0e3
- 结论：至少一个发布门禁失败，工作流没有执行 main 快进。

## generate.log 最后 200 行
```text
{"status": "generated", "project": "mini-commerce", "files": 300, "java": 120}
{"status": "final-fixes-applied", "files": 187, "java": 121}
{"status": "release-fixes-applied", "counts": {"files": 361, "markdown": 158, "java": 122, "sql": 10, "python": 20, "yaml": 23}, "aggregateSha256": "3be3b55fd20d5311dcd710d58f4f681b8e09dd530930595e9b5dc99c10f2a3c7"}
{"status": "completeness-fixes-v3-applied"}
{"status": "mapping-refined", "entries": 1281}
mini-commerce/infra/aws/terraform/versions.tf
[31m[31m╷[0m[0m
[31m│[0m [0m[1m[31mError: [0m[0m[1mInvalid character[0m
[31m│[0m [0m
[31m│[0m [0m[0m  on mini-commerce/infra/aws/terraform/main.tf line 15, in resource "aws_internet_gateway" "main":
[31m│[0m [0m  15: resource "aws_internet_gateway" "main" { vpc_id = aws_vpc.main.id[4m;[0m tags = { Name = local.name } }[0m
[31m│[0m [0m
[31m│[0m [0mThe ";" character is not valid. Use newlines to separate arguments and
[31m│[0m [0mblocks, and commas to separate items in collection values.
[31m╵[0m[0m
[0m[0m
[31m[31m╷[0m[0m
[31m│[0m [0m[1m[31mError: [0m[0m[1mInvalid single-argument block definition[0m
[31m│[0m [0m
[31m│[0m [0m[0m  on mini-commerce/infra/aws/terraform/main.tf line 15, in resource "aws_internet_gateway" "main":
[31m│[0m [0m  15: resource "aws_internet_gateway" "main" { vpc_id = aws_vpc.main.id[4m;[0m tags = { Name = local.name } }[0m
[31m│[0m [0m
[31m│[0m [0mA single-line block definition must end with a closing brace immediately
[31m│[0m [0mafter its single argument definition.
[31m╵[0m[0m
[0m[0m
[31m[31m╷[0m[0m
[31m│[0m [0m[1m[31mError: [0m[0m[1mInvalid character[0m
[31m│[0m [0m
[31m│[0m [0m[0m  on mini-commerce/infra/aws/terraform/outputs.tf line 2, in output "rds_endpoint":
[31m│[0m [0m   2: output "rds_endpoint" { value = aws_db_instance.postgres.address[4m;[0m sensitive = true }[0m
[31m│[0m [0m
[31m│[0m [0mThe ";" character is not valid. Use newlines to separate arguments and
[31m│[0m [0mblocks, and commas to separate items in collection values.
[31m╵[0m[0m
[0m[0m
[31m[31m╷[0m[0m
[31m│[0m [0m[1m[31mError: [0m[0m[1mInvalid single-argument block definition[0m
[31m│[0m [0m
[31m│[0m [0m[0m  on mini-commerce/infra/aws/terraform/outputs.tf line 2, in output "rds_endpoint":
[31m│[0m [0m   2: output "rds_endpoint" { value = aws_db_instance.postgres.address[4m;[0m sensitive = true }[0m
[31m│[0m [0m
[31m│[0m [0mA single-line block definition must end with a closing brace immediately
[31m│[0m [0mafter its single argument definition.
[31m╵[0m[0m
[0m[0m
[31m[31m╷[0m[0m
[31m│[0m [0m[1m[31mError: [0m[0m[1mInvalid character[0m
[31m│[0m [0m
[31m│[0m [0m[0m  on mini-commerce/infra/aws/terraform/variables.tf line 1, in variable "aws_region":
[31m│[0m [0m   1: variable "aws_region" { type = string[4m;[0m default = "ap-northeast-1" }[0m
[31m│[0m [0m
[31m│[0m [0mThe ";" character is not valid. Use newlines to separate arguments and
[31m│[0m [0mblocks, and commas to separate items in collection values.
[31m╵[0m[0m
[0m[0m
[31m[31m╷[0m[0m
[31m│[0m [0m[1m[31mError: [0m[0m[1mInvalid single-argument block definition[0m
[31m│[0m [0m
[31m│[0m [0m[0m  on mini-commerce/infra/aws/terraform/variables.tf line 1, in variable "aws_region":
[31m│[0m [0m   1: variable "aws_region" { type = string[4m;[0m default = "ap-northeast-1" }[0m
[31m│[0m [0m
[31m│[0m [0mA single-line block definition must end with a closing brace immediately
[31m│[0m [0mafter its single argument definition.
[31m╵[0m[0m
[0m[0m
{"status": "delivery-finalized", "counts": {"files": 366, "markdown": 159, "java": 123, "sql": 10, "python": 20, "yaml": 24}, "project": {"generatedAt": "2026-09-03T06:12:49.625214+00:00", "fileCount": 193, "javaMainFiles": 115, "javaTestFiles": 8, "migrations": ["V001__baseline.sql", "V002__operational_indexes.sql", "V003__refunds.sql"], "documentMappingEntries": 1281}, "aggregateSha256": "6fdfd438678b5f0e8a22ab23a60c630dbac828e414f67af7216858656aee5340"}
```

## static.log 最后 200 行
```text
{"status": "valid", "project": "mini-commerce"}
{
  "references": 47,
  "errors": []
}
{
  "passed": false,
  "checks": [
    {
      "name": "订单请求不接收客户端总价",
      "passed": false,
      "evidence": "OrderDtos"
    },
    {
      "name": "条件库存更新",
      "passed": true,
      "evidence": "InventoryRepository"
    },
    {
      "name": "Outbox 同工程存在",
      "passed": true,
      "evidence": "V001"
    },
    {
      "name": "MCP 拒绝 DDL",
      "passed": true,
      "evidence": "security.py"
    }
  ]
}
```
