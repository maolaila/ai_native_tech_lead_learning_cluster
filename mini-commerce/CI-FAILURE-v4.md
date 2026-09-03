# CI 失败报告（main 未更新）

- Workflow: https://github.com/maolaila/ai_native_tech_lead_learning_cluster/actions/runs/33722235398
- Commit: 70e16a0e428658ec9c04df1f9b2f0946fb1f81fb
- 结论：至少一个发布门禁失败；main 快进步骤未执行。

## finalize.log 最后 200 行
```text
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
{"status": "delivery-finalized", "counts": {"files": 370, "markdown": 160, "java": 123, "sql": 10, "python": 20, "yaml": 25}, "project": {"generatedAt": "2026-09-03T06:13:31.827131+00:00", "fileCount": 196, "javaMainFiles": 115, "javaTestFiles": 8, "migrations": ["V001__baseline.sql", "V002__operational_indexes.sql", "V003__refunds.sql"], "documentMappingEntries": 1281}, "aggregateSha256": "ea53cc7a596725302a6e926d5ed203debdd200f1395ca67ad1121020145318f7"}
```

## generate.log 最后 200 行
```text
{"status": "generated", "project": "mini-commerce", "files": 303, "java": 120}
{"status": "final-fixes-applied", "files": 189, "java": 121}
{"status": "release-fixes-applied", "counts": {"files": 364, "markdown": 159, "java": 122, "sql": 10, "python": 20, "yaml": 24}, "aggregateSha256": "12702cac2840864d829848ccb45560523b2a9a60b407b09d2165cfa6b35b6f7f"}
{"status": "completeness-fixes-v3-applied"}
{"status": "mapping-refined", "entries": 1281}
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
