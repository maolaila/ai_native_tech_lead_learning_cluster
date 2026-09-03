package com.example.minicommerce.payment.application;

import com.example.minicommerce.payment.infrastructure.PaymentWebhookRepository;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.util.UUID;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

/**
 * providerEventId 唯一约束使重复回调不会重复改变订单或库存。
 *
 * <p><strong>对应文档：</strong> {@code 05_auth_security/03_Web常见攻击.md}、 {@code
 * 07_rabbitmq/04_幂等与Outbox.md}、 {@code 11_system_design/04_韧性_Timeout_Retry_Circuit.md}。
 */
@Service
public class PaymentWebhookService {
    private final WebhookSignature signatures;
    private final PaymentWebhookRepository events;
    private final ObjectMapper json;
    private final PaymentTransactionService tx;

    public PaymentWebhookService(
            WebhookSignature s,
            PaymentWebhookRepository e,
            ObjectMapper j,
            PaymentTransactionService tx) {
        signatures = s;
        events = e;
        json = j;
        this.tx = tx;
    }

    @Transactional
    public void handle(String body, String signature) throws Exception {
        signatures.verify(body, signature);
        WebhookPayload p = json.readValue(body, WebhookPayload.class);
        if (!events.claim(p.eventId(), body)) return;
        if ("payment.succeeded".equals(p.type()))
            tx.apply(p.paymentId(), PaymentGateway.GatewayResult.success(p.providerReference()));
        else if ("payment.declined".equals(p.type()))
            tx.apply(
                    p.paymentId(),
                    PaymentGateway.GatewayResult.declined("provider webhook declined"));
    }

    public record WebhookPayload(
            String eventId, String type, UUID paymentId, String providerReference) {}
}
