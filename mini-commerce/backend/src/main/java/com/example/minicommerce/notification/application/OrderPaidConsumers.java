package com.example.minicommerce.notification.application;

import com.example.minicommerce.messaging.application.*;
import com.example.minicommerce.messaging.config.RabbitTopology;
import com.example.minicommerce.notification.infrastructure.*;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.math.BigDecimal;
import java.time.Clock;
import java.util.UUID;
import org.springframework.amqp.rabbit.annotation.RabbitListener;
import org.springframework.stereotype.Component;
import org.springframework.transaction.annotation.Transactional;

/**
 * 两个独立 Queue 表示通知和积分都要收到事件；同 Queue 多 Consumer 才是水平竞争消费。
 *
 * <p><strong>对应文档：</strong> {@code 07_rabbitmq/01_同步异步与事件边界.md}、 {@code
 * 07_rabbitmq/04_幂等与Outbox.md}。
 */
@Component
public class OrderPaidConsumers {
    private final ObjectMapper json;
    private final ProcessedMessageService processed;
    private final NotificationRepository notifications;
    private final PointsLedgerRepository points;
    private final Clock clock;

    public OrderPaidConsumers(
            ObjectMapper j,
            ProcessedMessageService p,
            NotificationRepository n,
            PointsLedgerRepository l,
            Clock c) {
        json = j;
        processed = p;
        notifications = n;
        points = l;
        clock = c;
    }

    @RabbitListener(queues = RabbitTopology.NOTIFICATION_Q)
    @Transactional
    public void notifyUser(String raw) throws Exception {
        EventEnvelope e = json.readValue(raw, EventEnvelope.class);
        if (!processed.claim("notification-order-paid", e.eventId())) return;
        Long user = e.payload().get("userId").asLong();
        notifications.save(
                new NotificationEntity(
                        user, "ORDER_PAID", "订单 " + e.aggregateId() + " 已支付", clock.instant()));
    }

    @RabbitListener(queues = RabbitTopology.POINTS_Q)
    @Transactional
    public void addPoints(String raw) throws Exception {
        EventEnvelope e = json.readValue(raw, EventEnvelope.class);
        if (!processed.claim("points-order-paid", e.eventId())) return;
        Long user = e.payload().get("userId").asLong();
        BigDecimal total = e.payload().get("total").decimalValue();
        points.save(
                new PointsLedgerEntity(
                        user,
                        UUID.fromString(e.aggregateId()),
                        total.divideToIntegralValue(BigDecimal.valueOf(100)).intValue(),
                        clock.instant()));
    }
}
