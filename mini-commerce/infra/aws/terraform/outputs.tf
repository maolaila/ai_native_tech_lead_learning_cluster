output "application_url" { value = "http://${aws_lb.app.dns_name}" }
output "rds_endpoint" { value = aws_db_instance.postgres.address; sensitive = true }
output "secret_arn" { value = aws_secretsmanager_secret.app.arn }
output "estimated_cost_warning" { value = "ALB、RDS、NAT、ElastiCache 即使低流量也持续计费。学习完成后运行 terraform destroy，并检查快照/EIP/日志/S3。" }
