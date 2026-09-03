from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
PROJECT = REPO / "mini-commerce"


def write(relative: str, content: str) -> None:
    path = REPO / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


# 防止“每个幂等键内部正确，但不同 Key 同时对同一订单扣款”的跨键并发漏洞。
repo = PROJECT / "backend/src/main/java/com/example/minicommerce/payment/infrastructure/PaymentAttemptRepository.java"
text = repo.read_text(encoding="utf-8")
needle = 'boolean existsByOrderIdAndStatusIn(UUID orderId, Collection<PaymentStatus> statuses);'
replacement = '''boolean existsByOrderIdAndStatusIn(UUID orderId, Collection<PaymentStatus> statuses);

    Optional<PaymentAttemptEntity> findFirstByOrderIdAndStatusInOrderByCreatedAtDesc(
        UUID orderId, Collection<PaymentStatus> statuses);'''
if needle not in text:
    raise SystemExit("PaymentAttemptRepository 补丁目标不存在")
repo.write_text(text.replace(needle, replacement), encoding="utf-8")

service = PROJECT / "backend/src/main/java/com/example/minicommerce/payment/application/PaymentTransactionService.java"
text = service.read_text(encoding="utf-8")
needle = '''if (order.getStatus() != OrderStatus.PENDING_PAYMENT) {
            throw new BusinessException(ErrorCode.ORDER_NOT_PAYABLE, "订单不可支付");
        }
        PaymentAttemptEntity payment = payments.saveAndFlush'''
replacement = '''if (order.getStatus() != OrderStatus.PENDING_PAYMENT) {
            throw new BusinessException(ErrorCode.ORDER_NOT_PAYABLE, "订单不可支付");
        }
        payments.findFirstByOrderIdAndStatusInOrderByCreatedAtDesc(orderId,
            java.util.EnumSet.of(PaymentStatus.INITIATED, PaymentStatus.PROCESSING, PaymentStatus.UNKNOWN, PaymentStatus.SUCCEEDED))
            .ifPresent(existing -> {
                throw new BusinessException(ErrorCode.IDEMPOTENCY_CONFLICT,
                    "该订单已有进行中、结果未知或已成功的支付，请查询原支付而不是创建新支付");
            });
        PaymentAttemptEntity payment = payments.saveAndFlush'''
if needle not in text:
    raise SystemExit("PaymentTransactionService 活跃支付补丁目标不存在")
service.write_text(text.replace(needle, replacement), encoding="utf-8")

# 全额退款模型中，一个成功支付只允许一个退款聚合；不同幂等键也不能重复退款。
refund_repo = PROJECT / "backend/src/main/java/com/example/minicommerce/refund/infrastructure/RefundRepository.java"
text = refund_repo.read_text(encoding="utf-8")
needle = 'Optional<RefundEntity> findByPaymentIdAndKey(UUID paymentId, String key);'
replacement = '''Optional<RefundEntity> findByPaymentIdAndKey(UUID paymentId, String key);

    Optional<RefundEntity> findByPaymentId(UUID paymentId);'''
if needle not in text:
    raise SystemExit("RefundRepository 补丁目标不存在")
refund_repo.write_text(text.replace(needle, replacement), encoding="utf-8")

refund_tx = PROJECT / "backend/src/main/java/com/example/minicommerce/refund/application/RefundTransactionService.java"
text = refund_tx.read_text(encoding="utf-8")
needle = '''Optional<RefundEntity> prior = refunds.findByPaymentIdAndKey(paymentId, key);
        if (prior.isPresent()) return view(prior.get());

        PaymentAttemptEntity payment'''
replacement = '''Optional<RefundEntity> prior = refunds.findByPaymentIdAndKey(paymentId, key);
        if (prior.isPresent()) return view(prior.get());
        refunds.findByPaymentId(paymentId).ifPresent(existing -> {
            throw new BusinessException(ErrorCode.IDEMPOTENCY_CONFLICT,
                "该支付已有退款流程；请使用原幂等键查询或继续对账");
        });

        PaymentAttemptEntity payment'''
if needle not in text:
    raise SystemExit("RefundTransactionService 补丁目标不存在")
refund_tx.write_text(text.replace(needle, replacement), encoding="utf-8")

migration = PROJECT / "backend/src/main/resources/db/migration/V003__refunds.sql"
text = migration.read_text(encoding="utf-8")
needle = 'constraint ux_refund_payment_key unique(payment_id,idempotency_key));'
replacement = '''constraint ux_refund_payment_key unique(payment_id,idempotency_key),
 constraint ux_refund_payment unique(payment_id));'''
if needle not in text:
    raise SystemExit("V003 唯一约束补丁目标不存在")
migration.write_text(text.replace(needle, replacement), encoding="utf-8")

migration1 = PROJECT / "backend/src/main/resources/db/migration/V001__baseline.sql"
text = migration1.read_text(encoding="utf-8")
needle = "create unique index ux_payment_success_per_order on payment_attempts(order_id) where status='SUCCEEDED';"
replacement = '''create unique index ux_payment_success_per_order on payment_attempts(order_id) where status='SUCCEEDED';
create unique index ux_payment_active_per_order on payment_attempts(order_id)
 where status in('INITIATED','PROCESSING','UNKNOWN','SUCCEEDED');'''
if needle not in text:
    raise SystemExit("V001 支付唯一索引补丁目标不存在")
migration1.write_text(text.replace(needle, replacement), encoding="utf-8")

# HTTP 层对象级授权证据：不是只测试一个 Policy 方法，而是经过 Security Filter、Controller 和 Exception Handler。
write("mini-commerce/backend/src/test/java/com/example/minicommerce/order/OrderObjectAuthorizationIT.java", r'''package com.example.minicommerce.order;

import static org.springframework.security.test.web.servlet.request.SecurityMockMvcRequestPostProcessors.user;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;
import com.example.minicommerce.identity.domain.UserRole;
import com.example.minicommerce.identity.infrastructure.UserEntity;
import com.example.minicommerce.identity.infrastructure.UserRepository;
import com.example.minicommerce.order.infrastructure.OrderEntity;
import com.example.minicommerce.order.infrastructure.OrderRepository;
import com.example.minicommerce.shared.security.UserPrincipal;
import com.example.minicommerce.support.AbstractPostgresIT;
import java.math.BigDecimal;
import java.time.Instant;
import java.util.UUID;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.test.web.servlet.MockMvc;

@AutoConfigureMockMvc
class OrderObjectAuthorizationIT extends AbstractPostgresIT {
    @Autowired MockMvc mvc;
    @Autowired UserRepository users;
    @Autowired OrderRepository orders;

    @Test
    void ordinaryUser_cannotReadAnotherUsersOrder() throws Exception {
        UserEntity owner = users.save(new UserEntity(UUID.randomUUID() + "@example.com", "owner", "hash", UserRole.USER));
        UserEntity intruder = users.save(new UserEntity(UUID.randomUUID() + "@example.com", "intruder", "hash", UserRole.USER));
        OrderEntity order = orders.save(new OrderEntity(UUID.randomUUID(), "AUTH-" + UUID.randomUUID(), owner.getId(),
            new BigDecimal("100.00"), BigDecimal.ZERO.setScale(2), new BigDecimal("100.00"), "JPY", null, Instant.now()));

        mvc.perform(get("/api/orders/{id}", order.getId()).with(user(UserPrincipal.from(intruder))))
            .andExpect(status().isForbidden())
            .andExpect(jsonPath("$.code").value("ACCESS_DENIED"));
    }
}
''')

# Jenkins 与 GitHub Actions 共用仓库内命令，避免把核心构建逻辑藏在平台 UI。
write("mini-commerce/Jenkinsfile", r'''pipeline {
  agent any
  options { timestamps(); disableConcurrentBuilds(abortPrevious: true) }
  stages {
    stage('Backend') {
      agent { docker { image 'maven:3.9.11-eclipse-temurin-21-alpine'; args '-v /var/run/docker.sock:/var/run/docker.sock' } }
      steps { dir('backend') { sh 'mvn -B -ntp verify' } }
      post { always { junit allowEmptyResults: true, testResults: 'backend/target/*-reports/*.xml' } }
    }
    stage('MCP') {
      agent { docker { image 'python:3.13-slim' } }
      steps { dir('mcp-server') { sh "pip install -e '.[dev]' && pytest -q" } }
    }
    stage('Static and IaC') {
      steps {
        sh 'python3 tools/check_learning_references.py'
        sh 'python3 ai-engineering/eval/run_static_eval.py'
        sh 'docker compose config >/dev/null'
      }
    }
  }
  post { always { archiveArtifacts allowEmptyArchive: true, artifacts: 'backend/target/*-reports/**,VALIDATION-REPORT.md' } }
}
''')

# 最小反向代理配置：前端不是学习重点，但仍能实践 Forwarded Header、Body Limit、Timeout 与 502/504 排障。
write("mini-commerce/infra/nginx/nginx.conf", r'''events {}
http {
  log_format structured escape=json '{"time":"$time_iso8601","requestId":"$request_id","method":"$request_method","uri":"$uri","status":$status,"upstreamTime":"$upstream_response_time"}';
  access_log /dev/stdout structured;
  error_log /dev/stderr warn;

  upstream commerce_api { server backend:8080; keepalive 32; }
  server {
    listen 8088;
    client_max_body_size 2m;
    location / {
      proxy_pass http://commerce_api;
      proxy_set_header Host $host;
      proxy_set_header X-Forwarded-Proto $scheme;
      proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
      proxy_set_header X-Request-Id $request_id;
      proxy_connect_timeout 1s;
      proxy_read_timeout 5s;
      proxy_send_timeout 5s;
    }
  }
}
''')

compose = PROJECT / "compose.yaml"
text = compose.read_text(encoding="utf-8")
needle = '''  mcp-server:
    profiles: [app]'''
replacement = '''  gateway:
    profiles: [app]
    image: nginx:1.29-alpine
    ports: ["${GATEWAY_PORT:-18088}:8088"]
    volumes: [./infra/nginx/nginx.conf:/etc/nginx/nginx.conf:ro]
    depends_on:
      backend: {condition: service_healthy}
    read_only: true
    tmpfs: [/var/cache/nginx, /var/run]
    security_opt: [no-new-privileges:true]
    cap_drop: [ALL]
    cap_add: [NET_BIND_SERVICE]
    networks: [commerce]

  mcp-server:
    profiles: [app]'''
if needle not in text:
    raise SystemExit("Compose gateway 补丁目标不存在")
compose.write_text(text.replace(needle, replacement), encoding="utf-8")

# 可审阅的 API 契约；实际 Controller 行为仍由 API Integration Test 验证。
write("mini-commerce/api/openapi.yaml", r'''openapi: 3.1.0
info:
  title: Mini Commerce API
  version: 1.0.0
  description: 学习工程的核心业务契约；错误响应使用 Problem Details + code + traceId。
servers: [{url: http://localhost:18088}]
paths:
  /api/auth/login:
    post:
      operationId: login
      requestBody: {required: true, content: {application/json: {schema: {$ref: '#/components/schemas/LoginRequest'}}}}
      responses: {'200': {description: 登录成功}, '401': {$ref: '#/components/responses/Problem'}}
  /api/products:
    get:
      operationId: listProducts
      responses: {'200': {description: 商品分页}}
  /api/orders:
    post:
      operationId: createOrder
      parameters:
        - {in: header, name: Idempotency-Key, required: true, schema: {type: string, maxLength: 128}}
      requestBody: {required: true, content: {application/json: {schema: {$ref: '#/components/schemas/CreateOrderRequest'}}}}
      responses:
        '201': {description: 创建成功}
        '400': {$ref: '#/components/responses/Problem'}
        '401': {$ref: '#/components/responses/Problem'}
        '409': {$ref: '#/components/responses/Problem'}
  /api/orders/{id}:
    get:
      operationId: getOrder
      parameters: [{in: path, name: id, required: true, schema: {type: string, format: uuid}}]
      responses: {'200': {description: 本人或授权角色读取}, '403': {$ref: '#/components/responses/Problem'}}
  /api/payments/orders/{orderId}:
    post:
      operationId: payOrder
      parameters:
        - {in: path, name: orderId, required: true, schema: {type: string, format: uuid}}
        - {in: header, name: Idempotency-Key, required: true, schema: {type: string, maxLength: 128}}
      responses: {'200': {description: 支付意图或已有结果}, '409': {$ref: '#/components/responses/Problem'}}
components:
  securitySchemes: {bearerAuth: {type: http, scheme: bearer, bearerFormat: JWT}}
  schemas:
    LoginRequest:
      type: object
      required: [email, password]
      properties: {email: {type: string, format: email}, password: {type: string}}
    CreateOrderRequest:
      type: object
      required: [items]
      properties:
        couponCode: {type: [string, 'null']}
        items:
          type: array
          minItems: 1
          maxItems: 50
          items:
            type: object
            required: [productId, quantity]
            properties: {productId: {type: integer, format: int64}, quantity: {type: integer, minimum: 1}}
    Problem:
      type: object
      required: [code, detail, traceId]
      properties: {code: {type: string}, detail: {type: string}, traceId: {type: string}}
  responses:
    Problem:
      description: 可预测业务或协议错误
      content: {application/problem+json: {schema: {$ref: '#/components/schemas/Problem'}}}
security: [{bearerAuth: []}]
''')

# 故障矩阵明确每个实验要观察的证据和恢复方式。
write("mini-commerce/labs/failure-matrix.md", r'''# 故障实验矩阵

| 故障 | 注入方式 | 预期业务结果 | 证据 | 恢复 |
|---|---|---|---|---|
| Redis 停机 | `docker compose stop redis` | 商品读受控回源；登录限流保守失败 | Cache Error、DB QPS、429/日志 | 恢复 Redis，观察回源下降 |
| RabbitMQ 停机 | stop rabbitmq | 订单仍提交，Outbox 积压 | orders/outbox、Publisher failed | 恢复 Broker，确认追平与消费者幂等 |
| 支付响应丢失 | paymentToken=`unknown` | 支付为 UNKNOWN，订单禁止取消/再次支付 | payment_attempts、409、审计 | 查询/模拟 Webhook 对账 |
| 库存竞争 | stock=1 并发 20 | 仅一个预留成功 | `InventoryConcurrencyIT`、inventory | 无人工修复；失败请求可换商品/数量 |
| DB 连接池耗尽 | `DB_POOL_MAX=2` + 慢事务 | Pending/Acquire 上升，不盲目扩池 | Hikari、Trace、pg_stat_activity | 终止根因事务/优化 SQL |
| 毒消息 | 发送非法 JSON | 有界重试后 DLQ | DLQ 数、失败原因、eventId | 修 Consumer 后受控重放 |
| 反向代理上游错误 | 改 nginx upstream | 502 且代理日志可定位 | gateway error log、backend health | 恢复服务名/端口 |
| SIGTERM | 支付/消费处理中 stop backend | 在途请求有界结束，未 Ack 消息重投 | shutdown log、DB/MQ | 新实例就绪后验证幂等 |
''')

print(json.dumps({"status": "completeness-fixes-v3-applied"}, ensure_ascii=False))
