package com.example.minicommerce.messaging.application;

import com.example.minicommerce.messaging.config.RabbitTopology;
import com.example.minicommerce.messaging.infrastructure.OutboxJdbcRepository;
import com.example.minicommerce.shared.config.AppProperties;
import io.micrometer.core.instrument.MeterRegistry;
import java.nio.charset.StandardCharsets;
import java.util.UUID;
import java.util.concurrent.TimeUnit;
import org.slf4j.*;
import org.springframework.amqp.core.*;
import org.springframework.amqp.rabbit.connection.CorrelationData;
import org.springframework.amqp.rabbit.core.RabbitTemplate;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;

/**
 * 可靠消息模块的应用用例编排层：{@code OutboxPublisher}。
 *
 * <p><strong>作用：</strong>编排一个完整业务用例，协调领域规则、仓储、外部端口与事务边界。
 *
 * <p><strong>为什么：</strong>事务应该围绕业务动作，而不是分散在 Controller 或每个 Repository 中。
 *
 * <p><strong>对应文档：</strong> {@code 07_rabbitmq/02_Exchange_Queue_Routing.md}、 {@code
 * 07_rabbitmq/03_Confirm_Ack_Retry_DLQ.md}、 {@code 07_rabbitmq/04_幂等与Outbox.md}。
 */
@Component
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
    private final String worker = UUID.randomUUID().toString();

    public OutboxPublisher(
            OutboxJdbcRepository r, RabbitTemplate rabbit, AppProperties p, MeterRegistry m) {
        repository = r;
        this.rabbit = rabbit;
        properties = p;
        metrics = m;
    }

    @Scheduled(fixedDelayString = "${app.outbox.poll-delay:500ms}")
    public void poll() {
        repository
                .claim(worker, properties.outbox().batchSize(), properties.outbox().lease())
                .forEach(this::publish);
    }

    private void publish(OutboxJdbcRepository.ClaimedEvent e) {
        try {
            MessageProperties mp = new MessageProperties();
            mp.setContentType(MessageProperties.CONTENT_TYPE_TEXT_PLAIN);
            mp.setContentEncoding(StandardCharsets.UTF_8.name());
            mp.setMessageId(e.eventId().toString());
            mp.setHeader("eventType", e.eventType());
            Message message = new Message(e.payload().getBytes(StandardCharsets.UTF_8), mp);
            CorrelationData correlation = new CorrelationData(e.eventId().toString());
            rabbit.send(RabbitTopology.EVENTS, e.eventType(), message, correlation);
            CorrelationData.Confirm confirm =
                    correlation
                            .getFuture()
                            .get(
                                    properties.outbox().publishTimeout().toMillis(),
                                    TimeUnit.MILLISECONDS);
            if (!confirm.isAck())
                throw new IllegalStateException("broker nack: " + confirm.getReason());
            repository.published(e.eventId());
            metrics.counter("commerce.outbox.published").increment();
        } catch (Exception ex) {
            log.warn(
                    "event=outbox_publish_failed eventId={} attempt={} reason={}",
                    e.eventId(),
                    e.attemptCount(),
                    ex.toString());
            repository.failed(e.eventId(), e.attemptCount(), ex.toString());
            metrics.counter("commerce.outbox.failed").increment();
        }
    }
}
