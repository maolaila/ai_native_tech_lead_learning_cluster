variable "aws_region" { type = string; default = "ap-northeast-1" }
variable "environment" { type = string; default = "learning" }
variable "owner" { type = string; default = "learner" }
variable "vpc_cidr" { type = string; default = "10.42.0.0/16" }
variable "container_image" { type = string; description = "已经在 CI 中验证并按 digest 固定的后端镜像" }
variable "db_name" { type = string; default = "commerce" }
variable "db_username" { type = string; default = "commerce_app"; sensitive = true }
variable "db_password" { type = string; sensitive = true; validation { condition = length(var.db_password) >= 16; error_message = "数据库密码至少 16 位。" } }
variable "jwt_secret_base64" { type = string; sensitive = true }
variable "enable_nat_gateway" { type = bool; default = false; description = "NAT Gateway 持续计费；学习环境默认关闭" }
variable "enable_elasticache" { type = bool; default = false; description = "学习完 Redis 云映射后再开启" }
variable "desired_count" { type = number; default = 2 }
