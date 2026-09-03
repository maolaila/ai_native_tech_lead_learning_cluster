data "aws_availability_zones" "available" { state = "available" }
data "aws_caller_identity" "current" {}

locals {
  name = "mini-commerce-${var.environment}"
  azs  = slice(data.aws_availability_zones.available.names, 0, 2)
}

resource "aws_vpc" "main" {
  cidr_block = var.vpc_cidr
  enable_dns_support = true
  enable_dns_hostnames = true
  tags = { Name = local.name }
}
resource "aws_internet_gateway" "main" { vpc_id = aws_vpc.main.id; tags = { Name = local.name } }

resource "aws_subnet" "public" {
  for_each = { for index, az in local.azs : az => index }
  vpc_id = aws_vpc.main.id
  availability_zone = each.key
  cidr_block = cidrsubnet(var.vpc_cidr, 8, each.value)
  map_public_ip_on_launch = true
  tags = { Name = "${local.name}-public-${each.key}", Tier = "public" }
}
resource "aws_subnet" "private" {
  for_each = { for index, az in local.azs : az => index }
  vpc_id = aws_vpc.main.id
  availability_zone = each.key
  cidr_block = cidrsubnet(var.vpc_cidr, 8, each.value + 10)
  tags = { Name = "${local.name}-private-${each.key}", Tier = "private" }
}
resource "aws_route_table" "public" { vpc_id = aws_vpc.main.id; route { cidr_block = "0.0.0.0/0"; gateway_id = aws_internet_gateway.main.id } }
resource "aws_route_table_association" "public" { for_each = aws_subnet.public; subnet_id = each.value.id; route_table_id = aws_route_table.public.id }

# NAT 是学习账单最常见的意外来源之一，因此默认关闭。生产私网任务通常需要 NAT 或 VPC Endpoint。
resource "aws_eip" "nat" { count = var.enable_nat_gateway ? 1 : 0; domain = "vpc"; depends_on = [aws_internet_gateway.main] }
resource "aws_nat_gateway" "main" { count = var.enable_nat_gateway ? 1 : 0; allocation_id = aws_eip.nat[0].id; subnet_id = values(aws_subnet.public)[0].id }
resource "aws_route_table" "private" {
  vpc_id = aws_vpc.main.id
  dynamic "route" { for_each = var.enable_nat_gateway ? [1] : []; content { cidr_block = "0.0.0.0/0"; nat_gateway_id = aws_nat_gateway.main[0].id } }
}
resource "aws_route_table_association" "private" { for_each = aws_subnet.private; subnet_id = each.value.id; route_table_id = aws_route_table.private.id }

resource "aws_security_group" "alb" {
  name = "${local.name}-alb"; vpc_id = aws_vpc.main.id
  ingress { description = "HTTP learning ingress"; from_port = 80; to_port = 80; protocol = "tcp"; cidr_blocks = ["0.0.0.0/0"] }
  egress { from_port = 0; to_port = 0; protocol = "-1"; cidr_blocks = ["0.0.0.0/0"] }
}
resource "aws_security_group" "app" {
  name = "${local.name}-app"; vpc_id = aws_vpc.main.id
  ingress { description = "Only ALB reaches application"; from_port = 8080; to_port = 8080; protocol = "tcp"; security_groups = [aws_security_group.alb.id] }
  egress { from_port = 0; to_port = 0; protocol = "-1"; cidr_blocks = ["0.0.0.0/0"] }
}
resource "aws_security_group" "db" {
  name = "${local.name}-db"; vpc_id = aws_vpc.main.id
  ingress { description = "Only application reaches PostgreSQL"; from_port = 5432; to_port = 5432; protocol = "tcp"; security_groups = [aws_security_group.app.id] }
}
resource "aws_security_group" "redis" {
  count = var.enable_elasticache ? 1 : 0; name = "${local.name}-redis"; vpc_id = aws_vpc.main.id
  ingress { description = "Only application reaches Redis"; from_port = 6379; to_port = 6379; protocol = "tcp"; security_groups = [aws_security_group.app.id] }
}

resource "aws_lb" "app" { name = substr(local.name,0,32); internal = false; load_balancer_type = "application"; security_groups = [aws_security_group.alb.id]; subnets = values(aws_subnet.public)[*].id }
resource "aws_lb_target_group" "app" { name = substr("${local.name}-app",0,32); port = 8080; protocol = "HTTP"; vpc_id = aws_vpc.main.id; target_type = "ip"; health_check { path = "/actuator/health/readiness"; matcher = "200" } }
resource "aws_lb_listener" "http" { load_balancer_arn = aws_lb.app.arn; port = 80; protocol = "HTTP"; default_action { type = "forward"; target_group_arn = aws_lb_target_group.app.arn } }
# 生产应使用 ACM 证书和 HTTPS Listener，并将 HTTP 重定向到 HTTPS。

resource "aws_db_subnet_group" "main" { name = local.name; subnet_ids = values(aws_subnet.private)[*].id }
resource "aws_db_instance" "postgres" {
  identifier = local.name
  engine = "postgres"
  engine_version = "17"
  instance_class = "db.t4g.micro"
  allocated_storage = 20
  max_allocated_storage = 100
  db_name = var.db_name
  username = var.db_username
  password = var.db_password
  db_subnet_group_name = aws_db_subnet_group.main.name
  vpc_security_group_ids = [aws_security_group.db.id]
  publicly_accessible = false
  storage_encrypted = true
  backup_retention_period = 7
  deletion_protection = false
  skip_final_snapshot = true # 仅学习环境；生产必须 final snapshot + deletion protection。
  multi_az = false           # 生产按 SLO 开启；学习环境控制成本。
  apply_immediately = true
}

resource "aws_elasticache_subnet_group" "main" { count = var.enable_elasticache ? 1 : 0; name = local.name; subnet_ids = values(aws_subnet.private)[*].id }
resource "aws_elasticache_replication_group" "redis" {
  count = var.enable_elasticache ? 1 : 0
  replication_group_id = local.name
  description = "Mini Commerce cache/session learning cluster"
  engine = "redis"
  node_type = "cache.t4g.micro"
  num_cache_clusters = 1
  subnet_group_name = aws_elasticache_subnet_group.main[0].name
  security_group_ids = [aws_security_group.redis[0].id]
  at_rest_encryption_enabled = true
  transit_encryption_enabled = true
}

resource "aws_secretsmanager_secret" "app" { name = "${local.name}/runtime"; recovery_window_in_days = 0 }
resource "aws_secretsmanager_secret_version" "app" {
  secret_id = aws_secretsmanager_secret.app.id
  secret_string = jsonencode({
    DATABASE_URL = "jdbc:postgresql://${aws_db_instance.postgres.address}:5432/${var.db_name}"
    DATABASE_USER = var.db_username
    DATABASE_PASSWORD = var.db_password
    JWT_SECRET_BASE64 = var.jwt_secret_base64
  })
}
resource "aws_cloudwatch_log_group" "app" { name = "/ecs/${local.name}"; retention_in_days = 14 }

resource "aws_iam_role" "execution" {
  name = "${local.name}-execution"
  assume_role_policy = jsonencode({Version="2012-10-17",Statement=[{Effect="Allow",Principal={Service="ecs-tasks.amazonaws.com"},Action="sts:AssumeRole"}]})
}
resource "aws_iam_role_policy_attachment" "execution" { role = aws_iam_role.execution.name; policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy" }
resource "aws_iam_role_policy" "read_secret" {
  role = aws_iam_role.execution.id
  policy = jsonencode({Version="2012-10-17",Statement=[{Effect="Allow",Action=["secretsmanager:GetSecretValue"],Resource=aws_secretsmanager_secret.app.arn}]})
}
resource "aws_iam_role" "task" {
  name = "${local.name}-task"
  assume_role_policy = jsonencode({Version="2012-10-17",Statement=[{Effect="Allow",Principal={Service="ecs-tasks.amazonaws.com"},Action="sts:AssumeRole"}]})
}

resource "aws_ecs_cluster" "main" { name = local.name; setting { name = "containerInsights"; value = "enabled" } }
resource "aws_ecs_task_definition" "app" {
  family = local.name
  requires_compatibilities = ["FARGATE"]
  network_mode = "awsvpc"
  cpu = 512
  memory = 1024
  execution_role_arn = aws_iam_role.execution.arn
  task_role_arn = aws_iam_role.task.arn
  container_definitions = jsonencode([{
    name="backend",image=var.container_image,essential=true,portMappings=[{containerPort=8080,protocol="tcp"}],
    secrets=[
      {name="DATABASE_URL",valueFrom="${aws_secretsmanager_secret.app.arn}:DATABASE_URL::"},
      {name="DATABASE_USER",valueFrom="${aws_secretsmanager_secret.app.arn}:DATABASE_USER::"},
      {name="DATABASE_PASSWORD",valueFrom="${aws_secretsmanager_secret.app.arn}:DATABASE_PASSWORD::"},
      {name="JWT_SECRET_BASE64",valueFrom="${aws_secretsmanager_secret.app.arn}:JWT_SECRET_BASE64::"}
    ],
    environment=[{name="SPRING_PROFILES_ACTIVE",value="prod"}],
    logConfiguration={logDriver="awslogs",options={"awslogs-group"=aws_cloudwatch_log_group.app.name,"awslogs-region"=var.aws_region,"awslogs-stream-prefix"="backend"}},
    healthCheck={command=["CMD-SHELL","curl -fsS http://localhost:8080/actuator/health/liveness || exit 1"],interval=30,timeout=5,retries=3,startPeriod=30}
  }])
}
resource "aws_ecs_service" "app" {
  name = "backend"; cluster = aws_ecs_cluster.main.id; task_definition = aws_ecs_task_definition.app.arn
  desired_count = var.desired_count; launch_type = "FARGATE"
  network_configuration { subnets = values(aws_subnet.private)[*].id; security_groups = [aws_security_group.app.id]; assign_public_ip = false }
  load_balancer { target_group_arn = aws_lb_target_group.app.arn; container_name = "backend"; container_port = 8080 }
  deployment_circuit_breaker { enable = true; rollback = true }
  depends_on = [aws_lb_listener.http]
}

resource "aws_appautoscaling_target" "ecs" { max_capacity = 6; min_capacity = 2; resource_id = "service/${aws_ecs_cluster.main.name}/${aws_ecs_service.app.name}"; scalable_dimension = "ecs:service:DesiredCount"; service_namespace = "ecs" }
resource "aws_appautoscaling_policy" "cpu" { name = "${local.name}-cpu"; policy_type = "TargetTrackingScaling"; resource_id = aws_appautoscaling_target.ecs.resource_id; scalable_dimension = aws_appautoscaling_target.ecs.scalable_dimension; service_namespace = aws_appautoscaling_target.ecs.service_namespace; target_tracking_scaling_policy_configuration { target_value = 60; predefined_metric_specification { predefined_metric_type = "ECSServiceAverageCPUUtilization" } } }

resource "aws_s3_bucket" "artifacts" { bucket_prefix = "${local.name}-artifacts-" }
resource "aws_s3_bucket_public_access_block" "artifacts" { bucket = aws_s3_bucket.artifacts.id; block_public_acls=true; block_public_policy=true; ignore_public_acls=true; restrict_public_buckets=true }
resource "aws_s3_bucket_versioning" "artifacts" { bucket = aws_s3_bucket.artifacts.id; versioning_configuration { status = "Enabled" } }
resource "aws_s3_bucket_server_side_encryption_configuration" "artifacts" { bucket = aws_s3_bucket.artifacts.id; rule { apply_server_side_encryption_by_default { sse_algorithm = "AES256" } } }
