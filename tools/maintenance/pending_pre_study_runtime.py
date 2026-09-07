"""One-use assertion-guarded runtime repairs; removed by the audit workflow."""
from pathlib import Path
root = Path.cwd()
j = root/'mini-commerce/backend/src/main/java/com/example/minicommerce'
def edit(name, old, new):
    p=j/name
    text=p.read_text(encoding='utf-8')
    assert old in text, (name, old)
    p.write_text(text.replace(old,new), encoding='utf-8')
edit('identity/application/AuthService.java','.trim().toLowerCase()', '.trim().toLowerCase(java.util.Locale.ROOT)')
edit('identity/application/AuthService.java','        String email = request.email()', '''        // BCrypt 的限制按 UTF-8 字节计算，不是 Java 字符数；中文可能占多个字节。
        if (request.password() == null || request.password().getBytes(StandardCharsets.UTF_8).length > 72) {
            throw new BusinessException(ErrorCode.VALIDATION_ERROR, "密码的 UTF-8 编码不能超过 72 字节");
        }
        String email = request.email()''')
edit('identity/infrastructure/RefreshTokenRepository.java','    Optional<RefreshTokenEntity> findByTokenHash(String tokenHash);','''    // 刷新和退出都要锁住同一条 Token，避免并发把一个旧 Token 轮换成两个新 Token。
    @org.springframework.data.jpa.repository.Lock(jakarta.persistence.LockModeType.PESSIMISTIC_WRITE)
    Optional<RefreshTokenEntity> findByTokenHash(String tokenHash);''')
edit('shared/security/SecurityConfiguration.java','            ApiSecurityHandlers handlers)', '            ApiSecurityHandlers handlers, org.springframework.core.env.Environment environment)')
edit('shared/security/SecurityConfiguration.java','''                .authorizeHttpRequests(
                        authorization ->
                                authorization''','''                .authorizeHttpRequests(authorization -> {
                    // 仅 local 学习环境允许容器内 Prometheus 匿名抓指标，Compose 端口绑定本机。
                    // 非 local 的监控端点要求管理员；生产应使用独立管理网络和机器凭证。
                    if (environment.matchesProfiles("local")) {
                        authorization.requestMatchers("/actuator/prometheus").permitAll();
                    }
                    authorization''')
edit('shared/security/SecurityConfiguration.java','                                        // 注册和登录必须允许未登录用户访问。','''                                        .requestMatchers("/actuator/**").hasRole("ADMIN")
                                        // 注册和登录必须允许未登录用户访问。''')
edit('shared/security/SecurityConfiguration.java','                                        .authenticated())','                                        .authenticated();\n                })')
edit('shared/web/CorrelationIdFilter.java','为每个入口请求建立 requestId/traceId','为每个入口请求建立 requestId（不冒充分布式 traceId）')
edit('shared/web/CorrelationIdFilter.java','''        try (MDC.MDCCloseable ignored1 = MDC.putCloseable("requestId", requestId);
                MDC.MDCCloseable ignored2 = MDC.putCloseable("traceId", requestId)) {''','''        // traceId 由 Micrometer/Tracing 创建；一个用户输入的 X-Request-Id 不能覆盖它。
        try (MDC.MDCCloseable ignored = MDC.putCloseable("requestId", requestId)) {''')
edit('messaging/infrastructure/OutboxJdbcRepository.java','    public void published(UUID id) {\n        jdbc.update(', '    public boolean published(UUID id, String worker, int attempt) {\n        return jdbc.update(')
edit('messaging/infrastructure/OutboxJdbcRepository.java','''last_error=null where event_id=?",
                id);''','''last_error=null where event_id=? and status='PUBLISHING' and locked_by=? and attempt_count=?",
                id, worker, attempt) == 1;''')
edit('messaging/infrastructure/OutboxJdbcRepository.java','    public void failed(UUID id, int attempt, String error)', '    public void failed(UUID id, String worker, int attempt, String error)')
edit('messaging/infrastructure/OutboxJdbcRepository.java','last_error=? where event_id=?",',"last_error=? where event_id=? and status='PUBLISHING' and locked_by=? and attempt_count=?\",")
edit('messaging/infrastructure/OutboxJdbcRepository.java','''                id);
    }

    public record''','''                id, worker, attempt);
    }

    public record''')
edit('messaging/infrastructure/OutboxJdbcRepository.java','    @Transactional\n    public boolean published', '''    // worker + attempt 是本次领取的凭证。旧 Worker 恢复时不能覆盖已经重新领取的事件。
    @Transactional
    public boolean published''')
edit('messaging/application/OutboxPublisher.java','new CorrelationData(event.eventId().toString())','new CorrelationData(event.eventId() + ":" + event.attemptCount())')
edit('messaging/application/OutboxPublisher.java','''            // 只有 Broker 明确 Ack 后，才把 Outbox 事件标记为已发布。
            repository.published(event.eventId());
            metrics.counter("commerce.outbox.published").increment();''','''            // Confirm Ack 只证明 Broker 接收；mandatory Return 表示没有路由到队列，仍然失败。
            if (correlation.getReturned() != null) {
                throw new IllegalStateException("消息未路由到任何队列: " + event.eventType());
            }
            if (repository.published(event.eventId(), worker, event.attemptCount())) {
                metrics.counter("commerce.outbox.published").increment();
            }''')
edit('messaging/application/OutboxPublisher.java','repository.failed(event.eventId(), event.attemptCount(), exception.toString());','repository.failed(event.eventId(), worker, event.attemptCount(), exception.toString());\n            if (exception instanceof InterruptedException) Thread.currentThread().interrupt();')
edit('messaging/application/ProcessedMessageService.java','    public boolean claim(', '''    // 去重标记必须和消费者的数据库副作用同成同败。
    @org.springframework.transaction.annotation.Transactional(propagation = org.springframework.transaction.annotation.Propagation.MANDATORY)
    public boolean claim(''')
edit('messaging/config/RabbitTopology.java','    public static final String CACHE_Q', '    public static final String LIFECYCLE_Q = "audit.order-lifecycle.v1";\n    public static final String CACHE_Q')
edit('messaging/config/RabbitTopology.java','    /** mandatory=true：','''    /** 创建、取消、退款也有实际订阅者，不把未路由的事件误报为已发布。 */
    @Bean
    Queue lifecycleQueue() { return durable(LIFECYCLE_Q); }

    @Bean
    Queue lifecycleDlq() { return QueueBuilder.durable(LIFECYCLE_Q + ".dlq").build(); }

    @Bean
    Binding lifecycleBinding(Queue lifecycleQueue, TopicExchange commerceExchange) {
        return BindingBuilder.bind(lifecycleQueue).to(commerceExchange).with("order.*.v1");
    }

    @Bean
    Binding lifecycleDead(Queue lifecycleDlq, DirectExchange deadLetterExchange) {
        return BindingBuilder.bind(lifecycleDlq).to(deadLetterExchange).with(LIFECYCLE_Q + ".dead");
    }

    /** mandatory=true：''')
(j/'messaging/application/OrderLifecycleConsumer.java').write_text('''package com.example.minicommerce.messaging.application;

import com.example.minicommerce.audit.application.AuditService;
import com.example.minicommerce.messaging.config.RabbitTopology;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.amqp.rabbit.annotation.RabbitListener;
import org.springframework.stereotype.Component;
import org.springframework.transaction.annotation.Transactional;

/**
 * 订单生命周期事件的审计订阅者：创建、付款、取消、退款都保留接收证据。
 * <p>这不是通知消费者；只有 order.paid.v1 才触发通知与积分。
 * <p><strong>对应文档：</strong>{@code 07_rabbitmq/04_幂等与Outbox.md}。
 */
@Component
public class OrderLifecycleConsumer {
    private final ObjectMapper json;
    private final ProcessedMessageService processed;
    private final AuditService audit;

    public OrderLifecycleConsumer(ObjectMapper json, ProcessedMessageService processed, AuditService audit) {
        this.json = json;
        this.processed = processed;
        this.audit = audit;
    }

    @RabbitListener(queues = RabbitTopology.LIFECYCLE_Q)
    @Transactional(rollbackFor = Exception.class)
    public void record(String raw) throws Exception {
        EventEnvelope event = json.readValue(raw, EventEnvelope.class);
        if (!processed.claim("audit-order-lifecycle", event.eventId())) return;
        audit.record(null, "ORDER_EVENT_RECEIVED", "ORDER", event.aggregateId(), null, event);
    }
}
''',encoding='utf-8')
edit('notification/application/OrderPaidConsumers.java','每满 100 元积 1 分。真实业务应把规则写成明确、可测试的领域策略。','每满 100 个订单币种单位积 1 分（JPY 是日元，不是人民币元）。不做汇率换算。')
edit('notification/application/OrderPaidConsumers.java','int earnedPoints =','long earnedPoints =')
edit('notification/application/OrderPaidConsumers.java','.intValue();','.longValueExact();')
edit('notification/infrastructure/PointsLedgerEntity.java','private int points;', 'private long points;')
edit('notification/infrastructure/PointsLedgerEntity.java','UUID o, int p, Instant n','UUID o, long p, Instant n')
edit('order/application/CreateOrderService.java','        UUID orderId = UUID.randomUUID();','''        if (subtotal.compareTo(new BigDecimal("99999999999999999.99")) > 0) {
            throw new BusinessException(ErrorCode.VALIDATION_ERROR, "订单金额超过当前系统支持范围");
        }
        UUID orderId = UUID.randomUUID();''')
edit('catalog/api/ProductDtos.java','@NotNull @DecimalMin("0.01") BigDecimal price', '@NotNull @DecimalMin("0.01") @Digits(integer = 17, fraction = 2) BigDecimal price')
p=root/'mini-commerce/backend/src/main/resources/application.yml'
s=p.read_text(encoding='utf-8').replace('connection-timeout: 1500ms', '# Hikari 的毫秒配置是 long 数字，不是 Duration 字符串。\n      connection-timeout: 1500').replace('validation-timeout: 1000ms','validation-timeout: 1000')
p.write_text(s,encoding='utf-8')
p=root/'mini-commerce/compose.yaml'
s=p.read_text(encoding='utf-8').replace('ports: ["${','ports: ["127.0.0.1:${').replace('      - "${RABBITMQ','      - "127.0.0.1:${RABBITMQ')
s=s.replace('volumes: [postgres-data:/var/lib/postgresql/data]', 'volumes:\n      - postgres-data:/var/lib/postgresql/data\n      - ./infra/postgres/init-readonly.sh:/docker-entrypoint-initdb.d/10-readonly.sh:ro')
s=s.replace('      TZ: UTC','      MCP_DATABASE_PASSWORD: ${MCP_DATABASE_PASSWORD:-commerce-readonly-local}\n      TZ: UTC')
s=s.replace('postgresql://${POSTGRES_USER:-commerce_app}:${POSTGRES_PASSWORD:-commerce-local}@postgres', 'postgresql://commerce_readonly:${MCP_DATABASE_PASSWORD:-commerce-readonly-local}@postgres')
p.write_text(s,encoding='utf-8')
p=root/'mini-commerce/infra/postgres/init-readonly.sh'
p.parent.mkdir(parents=True,exist_ok=True)
p.write_text('''#!/usr/bin/env bash
set -euo pipefail
# 仅新建的本地演示数据库执行。只读是数据库权限，不是变量名或客户端自律。
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" \\
  -v db="$POSTGRES_DB" -v app_user="$POSTGRES_USER" \\
  -v readonly_password="${MCP_DATABASE_PASSWORD:-commerce-readonly-local}" <<'SQL'
CREATE ROLE commerce_readonly LOGIN PASSWORD :'readonly_password';
GRANT CONNECT ON DATABASE :"db" TO commerce_readonly;
GRANT USAGE ON SCHEMA public TO commerce_readonly;
ALTER ROLE commerce_readonly SET default_transaction_read_only = on;
SQL
''',encoding='utf-8')
p=root/'mini-commerce/infra/observability/alerts.yml'
p.write_text(p.read_text(encoding='utf-8').replace('commerce_outbox_failed_total > 0','increase(commerce_outbox_failed_total[10m]) > 0'),encoding='utf-8')
(root/'mini-commerce/backend/src/main/resources/db/migration/V005__mcp_readonly_tables.sql').write_text('''-- 角色由本地 PostgreSQL 初始化脚本创建；测试数据库可能没有这个角色。
-- 只授权四张教学业务表，不授予账户、密码哈希、Refresh Token 或全部未来表的权限。
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'commerce_readonly') THEN
        GRANT SELECT ON products, inventory, orders, order_items TO commerce_readonly;
    END IF;
END
$$;
''',encoding='utf-8')
(root/'mini-commerce/backend/src/main/resources/db/migration/V006__points_bigint.sql').write_text('-- 积分使用 bigint，避免较大合法订单金额转换为 int 时静默溢出。\nalter table points_ledger alter column points type bigint;\n',encoding='utf-8')
