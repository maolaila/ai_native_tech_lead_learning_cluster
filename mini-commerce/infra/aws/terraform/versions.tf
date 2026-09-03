terraform {
  required_version = ">= 1.9.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }

    random = {
      source  = "hashicorp/random"
      version = "~> 3.7"
    }
  }
}

# Provider 决定 Terraform 通过哪套插件调用 AWS API。
provider "aws" {
  region = var.aws_region

  # 默认标签会自动加到支持 Tag 的资源上，便于成本、环境和负责人查询。
  default_tags {
    tags = {
      Project     = "mini-commerce"
      Environment = var.environment
      ManagedBy   = "terraform"
      Owner       = var.owner
    }
  }
}
