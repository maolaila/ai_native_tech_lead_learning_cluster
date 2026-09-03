# Output 是 terraform apply 完成后展示给使用者的重要结果。

output "application_url" {
  description = "通过 ALB 访问应用的学习环境 URL；生产环境应使用 HTTPS 和正式域名"
  value       = "http://${aws_lb.app.dns_name}"
}

output "rds_endpoint" {
  description = "RDS PostgreSQL 地址；标记为 sensitive，避免普通终端输出直接显示"
  value       = aws_db_instance.postgres.address
  sensitive   = true
}

output "secret_arn" {
  description = "应用运行时 Secret 的 ARN"
  value       = aws_secretsmanager_secret.app.arn
}

output "aws_account_id" {
  description = "当前 Terraform 凭证对应的 AWS Account ID，便于部署前再次核对账号"
  value       = data.aws_caller_identity.current.account_id
}

output "estimated_cost_warning" {
  description = "学习环境费用提醒"
  value       = "ALB、RDS、NAT、ElastiCache 即使低流量也可能持续计费。学习完成后运行 terraform destroy，并检查快照、EIP、日志和 S3。"
}
