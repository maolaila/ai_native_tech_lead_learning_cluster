package com.example.minicommerce.payment.infrastructure;

import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Repository;

/**
 * 登记支付方回调的 eventId，并判断这条回调是否已经处理过。
 *
 * <p><strong>作用：</strong>登记支付方回调的 eventId，并判断这条回调是否已经处理过。
 *
 * <p><strong>为什么：</strong>INSERT ON CONFLICT DO NOTHING 让并发相同事件只登记一次；登记与更新支付要在同一事务，失败才能一起撤销。
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
