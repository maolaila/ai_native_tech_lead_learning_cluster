package com.example.minicommerce.messaging.application;

import com.example.minicommerce.messaging.config.RabbitTopology;
import com.example.minicommerce.messaging.infrastructure.OutboxJdbcRepository;
import com.example.minicommerce.shared.config.AppProperties;
import io.micrometer.core.instrument.MeterRegistry;
import java.nio.charset.StandardCharsets;
import java.util.UUID;
import java.util.concurrent.TimeUnit;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.amqp.core.Message;
import org.springframework.amqp.core.MessageProperties;
import org.springframework.amqp.rabbit.connection.CorrelationData;
import org.springframework.amqp.rabbit.core.RabbitTemplate;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;

/**
 * 把 PostgreSQL Outbox 表中的待发送事件可靠地发布到 RabbitMQ。
 *
 * <p><strong>大白话：</strong>业务事务先把事件写进一张“待寄信清单”。这个后台组件定期领取清单中的事件，发送给 RabbitMQ，
 * 收到 Broker 确认后再把事件标记为已发布。
 *
 * <p><strong>为什么不能发送后立刻假设成功：</strong>网络可能中断，所以需要 Publisher Confirm。
 * 即使 RabbitMQ 已收到消息，程序也可能在标记数据库前宕机，因此同一事件仍可能再次发送，Consumer 必须幂等。
 *
 * <p><strong>对应文档：</strong> {@code 07_rabbitmq/03_Confirm_Ack_Retry_DLQ.md}、 {@code
 * 07_rabbitmq/04_幂等与Outbox.md}、 {@code mini-commerce/docs/REQUEST-TO-DATABASE-WALKTHROUGH.md}。
 */
// @Component：让 Spring 创建并管理这个后台发布组件。
@Component
// 只有 app.outbox.publisher-enabled=true 时启用；没有配置时按 matchIfMissing=true 默认启用。
@ConditionalOnProperty(
        name = "app.outbox.publisher-enabled",
        havingValue = "true",
        matchIfMissing = true)
public class OutboxPublisher {
    private static final Logger log = LoggerFactory.getLogger(OutboxPublisher.class);

    private final OutboxJdbcRepository repository;
    private final RabbitTemplate rabbit;
    private final AppProperties properties;
    private final MeterRegistry metrics;

    // 每个应用实例有自己的 worker ID，领取事件时可知道当前由哪个实例处理。
    private final String worker = UUID.randomUUID().toString();

    public OutboxPublisher(
            OutboxJdbcRepository repository,
            RabbitTemplate rabbit,
            AppProperties properties,
            MeterRegistry metrics) {
        this.repository = repository;
        this.rabbit = rabbit;
        this.properties = properties;
        this.metrics = metrics;
    }

    /**
     * 定期领取一批待发布事件。
     *
     * <p>{@code fixedDelayString} 表示上一轮结束后等待指定时间，再启动下一轮，不是从上一轮开始时固定计时。
     */
    // @Scheduled：Spring 按配置间隔自动调用，不需要 Controller 或用户手工触发。
    @Scheduled(fixedDelayString = "${app.outbox.poll-delay:500ms}")
    public void poll() {
        repository
                .claim(
                        worker,
                        properties.outbox().batchSize(),
                        properties.outbox().lease())
                .forEach(this::publish);
    }

    /** 发送单条事件、等待 RabbitMQ 确认，并记录成功或失败。 */
    private void publish(OutboxJdbcRepository.ClaimedEvent event) {
        try {
            MessageProperties messageProperties = new MessageProperties();
            messageProperties.setContentType(MessageProperties.CONTENT_TYPE_TEXT_PLAIN);
            messageProperties.setContentEncoding(StandardCharsets.UTF_8.name());
            // 使用稳定 eventId 作为 messageId，方便 Consumer 去重和日志排查。
            messageProperties.setMessageId(event.eventId().toString());
            messageProperties.setHeader("eventType", event.eventType());

            Message message =
                    new Message(
                            event.payload().getBytes(StandardCharsets.UTF_8),
                            messageProperties);
            CorrelationData correlation =
                    new CorrelationData(event.eventId().toString());

            // EVENTS 是 Exchange，eventType 同时作为 Routing Key。
            rabbit.send(
                    RabbitTopology.EVENTS,
                    event.eventType(),
                    message,
                    correlation);

            // 最多等待配置的 publishTimeout；不能无限占住发布线程。
            CorrelationData.Confirm confirm =
                    correlation
                            .getFuture()
                            .get(
                                    properties.outbox().publishTimeout().toMillis(),
                                    TimeUnit.MILLISECONDS);

            if (!confirm.isAck()) {
                throw new IllegalStateException("broker nack: " + confirm.getReason());
            }

            // 只有 Broker 明确 Ack 后，才把 Outbox 事件标记为已发布。
            repository.published(event.eventId());
            metrics.counter("commerce.outbox.published").increment();
        } catch (Exception exception) {
            // 失败不删除事件，记录次数和原因，留给下一轮按重试策略继续处理。
            log.warn(
                    "event=outbox_publish_failed eventId={} attempt={} reason={}",
                    event.eventId(),
                    event.attemptCount(),
                    exception.toString());
            repository.failed(
                    event.eventId(), event.attemptCount(), exception.toString());
            metrics.counter("commerce.outbox.failed").increment();
        }
    }
}
