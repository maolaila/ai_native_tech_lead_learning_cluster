# 变量可以理解成“运行 Terraform 前需要提供或可以覆盖的配置”。
# 敏感变量不会在普通输出中直接显示，但仍可能进入 Terraform State，因此 State 必须妥善保护。

variable "aws_region" {
  description = "部署资源的 AWS Region"
  type        = string
  default     = "ap-northeast-1"
}

variable "environment" {
  description = "环境名称，会进入资源命名和标签，例如 learning、staging 或 prod"
  type        = string
  default     = "learning"
}

variable "owner" {
  description = "资源负责人标签，方便成本和责任归属"
  type        = string
  default     = "learner"
}

variable "vpc_cidr" {
  description = "VPC 的私有网络地址范围"
  type        = string
  default     = "10.42.0.0/16"
}

variable "container_image" {
  description = "已经在 CI 中验证并最好按 digest 固定的后端镜像"
  type        = string
}

variable "db_name" {
  description = "PostgreSQL 数据库名称"
  type        = string
  default     = "commerce"
}

variable "db_username" {
  description = "应用连接 PostgreSQL 使用的账号"
  type        = string
  default     = "commerce_app"
  sensitive   = true
}

variable "db_password" {
  description = "应用连接 PostgreSQL 使用的密码"
  type        = string
  sensitive   = true

  validation {
    condition     = length(var.db_password) >= 16
    error_message = "数据库密码至少 16 位。"
  }
}

variable "jwt_secret_base64" {
  description = "Base64 编码的 JWT HMAC 签名密钥；不能提交真实生产值"
  type        = string
  sensitive   = true

  validation {
    condition     = length(var.jwt_secret_base64) >= 44
    error_message = "JWT Base64 密钥过短，应至少能表达 256 bit 随机密钥。"
  }
}

variable "enable_nat_gateway" {
  description = "NAT Gateway 会持续计费；学习环境默认关闭"
  type        = bool
  default     = false
}

variable "enable_elasticache" {
  description = "学习完 Redis 云映射后再开启，避免不必要费用"
  type        = bool
  default     = false
}

variable "desired_count" {
  description = "ECS Service 期望运行的后端任务数量"
  type        = number
  default     = 2

  validation {
    condition     = var.desired_count >= 1
    error_message = "desired_count 必须至少为 1。"
  }
}
