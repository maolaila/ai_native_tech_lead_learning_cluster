# AWS 学习基线

对应文档：`12_cloud_aws/*`。

映射：ALB → ECS/Fargate → RDS PostgreSQL；可选 ElastiCache；Secrets Manager 注入运行凭证；CloudWatch Logs；S3 保存产物/附件。数据库和 Redis 位于私有子网，Security Group 通过来源 SG 而不是公网 CIDR 授权。

## 使用

```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars
terraform init
terraform fmt -check
terraform validate
terraform plan
```

`apply` 前先配置 AWS Budget。默认关闭 NAT Gateway 和 ElastiCache，但 ALB/RDS 仍持续计费。学习结束运行 `terraform destroy`，随后检查 RDS 快照、EIP、Log Group、S3 对象及 Secrets Manager 是否仍存在。

此目录是中小系统的教学基线，不是所有公司的生产模板。生产需补充 HTTPS/ACM、WAF、Route 53、Multi-AZ、备份恢复验证、RabbitMQ/SQS 选型、OIDC CI Role、告警、合规和组织级 IaC 模块。
