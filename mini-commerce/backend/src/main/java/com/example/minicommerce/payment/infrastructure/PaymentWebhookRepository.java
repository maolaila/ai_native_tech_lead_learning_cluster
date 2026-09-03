package com.example.minicommerce.payment.infrastructure;

import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Repository;

/**
 * 支付模块的基础设施适配层：{@code PaymentWebhookRepository}。
 *
 * <p><strong>作用：</strong>负责 JPA、SQL、Redis、RabbitMQ 或外部系统等技术实现，并把技术细节隔离在业务边界之外。
 *
 * <p><strong>为什么：</strong>数据库表和框架会变化；隔离适配器可以避免这些变化扩散到业务规则和 API 契约。
 *
 * <p><strong>对应文档：</strong> {@code 05_auth_security/03_Web常见攻击.md}、 {@code
 * 07_rabbitmq/04_幂等与Outbox.md}、 {@code 11_system_design/04_韧性_Timeout_Retry_Circuit.md}。
 */
@Repository
public class PaymentWebhookRepository {
    private final JdbcTemplate jdbc;

    public PaymentWebhookRepository(JdbcTemplate j) {
        jdbc = j;
    }

    public boolean claim(String eventId, String payload) {
        return jdbc.update(
                        "insert into payment_webhook_events(provider_event_id,payload,received_at) values (?,?,now()) on conflict do nothing",
                        eventId,
                        payload)
                == 1;
    }
}
