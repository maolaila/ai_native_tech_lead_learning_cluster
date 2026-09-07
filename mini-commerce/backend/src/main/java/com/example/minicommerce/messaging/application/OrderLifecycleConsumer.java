package com.example.minicommerce.messaging.application;

import com.example.minicommerce.audit.application.AuditService;
import com.example.minicommerce.messaging.config.RabbitTopology;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.amqp.rabbit.annotation.RabbitListener;
import org.springframework.stereotype.Component;
import org.springframework.transaction.annotation.Transactional;

/**
 * 订单生命周期事件的审计订阅者：创建、付款、取消、退款都保留接收证据。
 *
 * <p>这不是通知消费者；只有 order.paid.v1 才触发通知与积分。
 *
 * <p><strong>对应文档：</strong>{@code 07_rabbitmq/04_幂等与Outbox.md}。
 */
@Component
public class OrderLifecycleConsumer {
    private final ObjectMapper json;
    private final ProcessedMessageService processed;
    private final AuditService audit;

    public OrderLifecycleConsumer(
            ObjectMapper json, ProcessedMessageService processed, AuditService audit) {
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
