package com.example.minicommerce;

import static org.assertj.core.api.Assertions.*;
import static org.mockito.ArgumentMatchers.*;
import static org.mockito.Mockito.*;

import com.example.minicommerce.catalog.application.ProductCacheService;
import com.example.minicommerce.messaging.application.OutboxPublisher;
import com.example.minicommerce.messaging.infrastructure.OutboxJdbcRepository;
import com.example.minicommerce.shared.config.AppProperties;
import com.example.minicommerce.shared.redis.RedisLockService;
import com.fasterxml.jackson.databind.ObjectMapper;
import io.micrometer.core.instrument.simple.SimpleMeterRegistry;
import java.time.Duration;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import java.util.concurrent.atomic.AtomicInteger;
import org.junit.jupiter.api.Test;
import org.springframework.amqp.core.*;
import org.springframework.amqp.rabbit.connection.CorrelationData;
import org.springframework.amqp.rabbit.core.RabbitTemplate;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.data.redis.core.ValueOperations;

/**
 * 缓存与消息边界回归：模拟准确的依赖故障，避免“捕获异常后再调用一次”隐藏副作用。
 * 对应文档：06_redis/03_穿透_击穿_雪崩与一致性.md、07_rabbitmq/03_Confirm_Ack_Retry_DLQ.md。
 */
class InfrastructureReadinessTest {
    private AppProperties properties() {
        return new AppProperties(
                null,
                null,
                new AppProperties.Cache(
                        Duration.ofMinutes(1), Duration.ofSeconds(5), Duration.ofSeconds(1)),
                new AppProperties.Outbox(
                        5, Duration.ofSeconds(30), Duration.ofSeconds(1), Duration.ofSeconds(1)));
    }

    @Test
    @SuppressWarnings("unchecked")
    void failedCacheWriteNeverRepeatsDatabaseRead() {
        var redis = mock(StringRedisTemplate.class);
        ValueOperations<String, String> values = mock(ValueOperations.class);
        when(redis.opsForValue()).thenReturn(values);
        var locks = mock(RedisLockService.class);
        when(locks.tryLock(anyString(), any()))
                .thenReturn(new RedisLockService.LockHandle("key", "owner"));
        doThrow(new RuntimeException("redis down"))
                .when(values)
                .set(anyString(), anyString(), any(Duration.class));
        var cache = new ProductCacheService(redis, new ObjectMapper(), properties(), locks);
        AtomicInteger calls = new AtomicInteger();
        assertThat(
                        cache.get(
                                1L,
                                () -> {
                                    calls.incrementAndGet();
                                    return Optional.empty();
                                }))
                .isEmpty();
        assertThat(calls).hasValue(1);
    }

    @Test
    @SuppressWarnings("unchecked")
    void failedDatabaseReadIsNotRetriedByCacheCatch() {
        var redis = mock(StringRedisTemplate.class);
        when(redis.opsForValue()).thenReturn(mock(ValueOperations.class));
        var locks = mock(RedisLockService.class);
        when(locks.tryLock(anyString(), any()))
                .thenReturn(new RedisLockService.LockHandle("key", "owner"));
        var cache = new ProductCacheService(redis, new ObjectMapper(), properties(), locks);
        AtomicInteger calls = new AtomicInteger();
        var failure = new IllegalStateException("database failure");
        assertThatThrownBy(
                        () ->
                                cache.get(
                                        1L,
                                        () -> {
                                            calls.incrementAndGet();
                                            throw failure;
                                        }))
                .isSameAs(failure);
        assertThat(calls).hasValue(1);
    }

    @Test
    @SuppressWarnings("unchecked")
    void anotherInstanceLoadingDoesNotCauseUnboundedFallback() {
        var redis = mock(StringRedisTemplate.class);
        when(redis.opsForValue()).thenReturn(mock(ValueOperations.class));
        var cache =
                new ProductCacheService(
                        redis, new ObjectMapper(), properties(), mock(RedisLockService.class));
        AtomicInteger calls = new AtomicInteger();
        assertThatThrownBy(
                        () ->
                                cache.get(
                                        1L,
                                        () -> {
                                            calls.incrementAndGet();
                                            return Optional.empty();
                                        }))
                .isInstanceOf(com.example.minicommerce.shared.error.BusinessException.class);
        assertThat(calls).hasValue(0);
    }

    @Test
    void brokerAckWithReturnDoesNotMarkOutboxPublished() {
        var repository = mock(OutboxJdbcRepository.class);
        var rabbit = mock(RabbitTemplate.class);
        var event =
                new OutboxJdbcRepository.ClaimedEvent(UUID.randomUUID(), "not.routed.v1", "{}", 1);
        when(repository.claim(anyString(), anyInt(), any())).thenReturn(List.of(event));
        doAnswer(
                        invocation -> {
                            CorrelationData data = invocation.getArgument(3);
                            data.setReturned(
                                    new ReturnedMessage(
                                            invocation.getArgument(2),
                                            312,
                                            "NO_ROUTE",
                                            "commerce.events",
                                            "not.routed.v1"));
                            data.getFuture().complete(new CorrelationData.Confirm(true, null));
                            return null;
                        })
                .when(rabbit)
                .send(anyString(), anyString(), any(Message.class), any(CorrelationData.class));
        new OutboxPublisher(repository, rabbit, properties(), new SimpleMeterRegistry()).poll();
        verify(repository, never()).published(any(), anyString(), anyInt());
        verify(repository).failed(eq(event.eventId()), anyString(), eq(1), anyString());
    }

    @Test
    void brokerAckWithoutReturnCanMarkOutboxPublished() {
        var repository = mock(OutboxJdbcRepository.class);
        var rabbit = mock(RabbitTemplate.class);
        var event =
                new OutboxJdbcRepository.ClaimedEvent(
                        UUID.randomUUID(), "order.created.v1", "{}", 1);
        when(repository.claim(anyString(), anyInt(), any())).thenReturn(List.of(event));
        doAnswer(
                        invocation -> {
                            CorrelationData data = invocation.getArgument(3);
                            data.getFuture().complete(new CorrelationData.Confirm(true, null));
                            return null;
                        })
                .when(rabbit)
                .send(anyString(), anyString(), any(Message.class), any(CorrelationData.class));
        new OutboxPublisher(repository, rabbit, properties(), new SimpleMeterRegistry()).poll();
        verify(repository).published(eq(event.eventId()), anyString(), eq(1));
        verify(repository, never()).failed(any(), anyString(), anyInt(), anyString());
    }

    /** 使用真实 Prometheus 导出器，不能用 SimpleMeterRegistry 代替命名验证。 */
    @Test
    void orderCounterExportsTheNameUsedByTheRuntimeProbe() {
        // 本版本 MeterRegistry 有 close()，但没有实现 AutoCloseable，不能放进 try(...)。
        var registry =
                new io.micrometer.prometheusmetrics.PrometheusMeterRegistry(
                        io.micrometer.prometheusmetrics.PrometheusConfig.DEFAULT);
        try {
            registry.counter(
                            com.example.minicommerce.order.application.CreateOrderService
                                    .CREATION_METRIC)
                    .increment();
            assertThat(registry.scrape()).contains("commerce_orders_creation_total 1.0");
        } finally {
            registry.close();
        }
    }
}
