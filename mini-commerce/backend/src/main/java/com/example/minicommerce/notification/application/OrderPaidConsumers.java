package com.example.minicommerce.notification.application;

import com.example.minicommerce.messaging.application.EventEnvelope;
import com.example.minicommerce.messaging.application.ProcessedMessageService;
import com.example.minicommerce.messaging.config.RabbitTopology;
import com.example.minicommerce.notification.infrastructure.NotificationEntity;
import com.example.minicommerce.notification.infrastructure.NotificationRepository;
import com.example.minicommerce.notification.infrastructure.PointsLedgerEntity;
import com.example.minicommerce.notification.infrastructure.PointsLedgerRepository;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.math.BigDecimal;
import java.time.Clock;
import java.util.UUID;
import org.springframework.amqp.rabbit.annotation.RabbitListener;
import org.springframework.stereotype.Component;
import org.springframework.transaction.annotation.Transactional;

/**
 * 处理“订单已支付”事件的两个独立消费者：创建通知和增加积分。
 *
 * <p><strong>为什么是两个 Queue：</strong>通知和积分都要收到同一个事件。两个独立 Queue 各保存一份消息；
 * 同一个 Queue 上放多个 Consumer 通常是为了分摊工作，一条消息只会交给其中一个 Consumer。
 *
 * <p><strong>为什么必须幂等：</strong>Consumer 可能已经提交数据库，但在发送 Ack 前宕机。RabbitMQ 会再次投递同一消息，
 * 所以代码先按 {@code eventId} 领取处理权，已经处理过就直接返回。
 *
 * <p><strong>对应文档：</strong> {@code 07_rabbitmq/01_同步异步与事件边界.md}、 {@code
 * 07_rabbitmq/04_幂等与Outbox.md}、 {@code mini-commerce/docs/BACKEND-TERMS-PLAIN-CHINESE.md}。
 */
@Component
public class OrderPaidConsumers {
    private final ObjectMapper json;
    private final ProcessedMessageService processed;
    private final NotificationRepository notifications;
    private final PointsLedgerRepository points;
    private final Clock clock;

    public OrderPaidConsumers(
            ObjectMapper json,
            ProcessedMessageService processed,
            NotificationRepository notifications,
            PointsLedgerRepository points,
            Clock clock) {
        this.json = json;
        this.processed = processed;
        this.notifications = notifications;
        this.points = points;
        this.clock = clock;
    }

    /**
     * 创建站内通知。
     *
     * <p>{@code @RabbitListener} 让 Spring 在通知队列有消息时自动调用本方法。
     * {@code @Transactional} 让“消息去重记录”和“保存通知”一起提交或一起回滚。
     */
    @RabbitListener(queues = RabbitTopology.NOTIFICATION_Q)
    @Transactional
    public void notifyUser(String rawMessage) throws Exception {
        EventEnvelope event = json.readValue(rawMessage, EventEnvelope.class);

        // claim 返回 false 表示这个 Consumer 业务已经处理过同一 eventId。
        if (!processed.claim("notification-order-paid", event.eventId())) {
            return;
        }

        Long userId = event.payload().get("userId").asLong();
        notifications.save(
                new NotificationEntity(
                        userId,
                        "ORDER_PAID",
                        "订单 " + event.aggregateId() + " 已支付",
                        clock.instant()));
    }

    /**
     * 增加积分。
     *
     * <p>积分有独立的 Consumer 名称和去重范围，因此通知成功不会错误地让积分消息被当成已处理。
     */
    @RabbitListener(queues = RabbitTopology.POINTS_Q)
    @Transactional
    public void addPoints(String rawMessage) throws Exception {
        EventEnvelope event = json.readValue(rawMessage, EventEnvelope.class);

        if (!processed.claim("points-order-paid", event.eventId())) {
            return;
        }

        Long userId = event.payload().get("userId").asLong();
        BigDecimal total = event.payload().get("total").decimalValue();

        // 当前演示规则：每满 100 元积 1 分。真实业务应把规则写成明确、可测试的领域策略。
        int earnedPoints =
                total.divideToIntegralValue(BigDecimal.valueOf(100)).intValue();

        points.save(
                new PointsLedgerEntity(
                        userId,
                        UUID.fromString(event.aggregateId()),
                        earnedPoints,
                        clock.instant()));
    }
}
