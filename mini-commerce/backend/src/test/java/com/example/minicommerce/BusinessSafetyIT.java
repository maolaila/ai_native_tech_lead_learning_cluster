package com.example.minicommerce;

import static org.assertj.core.api.Assertions.*;
import static org.mockito.ArgumentMatchers.*;
import static org.mockito.Mockito.when;
import static org.springframework.security.test.web.servlet.request.SecurityMockMvcRequestPostProcessors.user;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

import com.example.minicommerce.catalog.infrastructure.*;
import com.example.minicommerce.identity.domain.UserRole;
import com.example.minicommerce.identity.infrastructure.*;
import com.example.minicommerce.inventory.infrastructure.*;
import com.example.minicommerce.order.api.OrderDtos.*;
import com.example.minicommerce.order.application.*;
import com.example.minicommerce.payment.application.*;
import com.example.minicommerce.refund.application.RefundService;
import com.example.minicommerce.shared.error.BusinessException;
import com.example.minicommerce.shared.redis.RateLimitService;
import com.example.minicommerce.shared.security.UserPrincipal;
import com.example.minicommerce.support.AbstractPostgresIT;
import java.math.BigDecimal;
import java.util.*;
import org.junit.jupiter.api.*;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.test.context.bean.override.mockito.MockitoBean;
import org.springframework.test.web.servlet.MockMvc;

/**
 * 业务安全回归：测试最终数据库事实、重复请求和真正的并发，而不只看返回值。 对应文档：mini-commerce/docs/testing-strategy.md。
 * 不给测试方法添加事务，避免测试本身掩盖业务入口缺少事务的问题。
 */
@AutoConfigureMockMvc
class BusinessSafetyIT extends AbstractPostgresIT {
    @Autowired UserRepository users;
    @Autowired ProductRepository products;
    @Autowired InventoryRepository inventory;
    @Autowired CreateOrderService createOrders;
    @Autowired OrderCommandService commands;
    @Autowired PaymentOrchestrator paymentFlow;
    @Autowired PaymentTransactionService paymentTransactions;
    @Autowired RefundService refunds;
    @Autowired JdbcTemplate jdbc;
    @Autowired MockMvc http;
    @MockitoBean RateLimitService rateLimits;
    @Autowired com.example.minicommerce.identity.application.AuthService authentication;
    @Autowired com.example.minicommerce.notification.application.OrderPaidConsumers consumers;
    @Autowired com.example.minicommerce.messaging.infrastructure.OutboxJdbcRepository outboxJobs;
    @Autowired com.fasterxml.jackson.databind.ObjectMapper json;
    @Autowired org.springframework.core.env.Environment environment;
    UserPrincipal buyer;
    Long productId;

    @BeforeEach
    void prepareIndependentData() {
        var account =
                users.save(
                        new UserEntity(
                                UUID.randomUUID() + "@example.com",
                                "buyer",
                                "hash",
                                UserRole.USER));
        buyer = UserPrincipal.from(account);
        var product =
                new ProductEntity(
                        "SKU-" + UUID.randomUUID(),
                        "验收商品",
                        "test",
                        new BigDecimal("200.00"),
                        "CNY");
        product.publish();
        product = products.saveAndFlush(product);
        productId = product.getId();
        inventory.saveAndFlush(new InventoryEntity(productId, 10));
        // 本组检查 HTTP 契约；真实 Redis 与限流在 Compose 和独立测试中验证。
        when(rateLimits.allow(anyString(), anyInt(), any(), anyBoolean())).thenReturn(true);
    }

    private OrderResponse create(String key) {
        return createOrders.create(
                buyer.id(),
                key,
                new CreateOrderRequest(List.of(new OrderLineRequest(productId, 1)), null));
    }

    @Test
    void testProfileReallyInheritsRuntimeConfiguration() {
        assertThat(environment.getProperty("spring.jpa.hibernate.ddl-auto")).isEqualTo("validate");
        assertThat(environment.getProperty("spring.jpa.open-in-view")).isEqualTo("false");
        assertThat(environment.getProperty("spring.datasource.hikari.connection-timeout"))
                .isEqualTo("1500");
    }

    @Test
    void idempotencyConflictRollsBackWithoutTakingMoreStock() {
        create("fingerprint");
        var changed = new CreateOrderRequest(List.of(new OrderLineRequest(productId, 2)), null);
        assertThatThrownBy(() -> createOrders.create(buyer.id(), "fingerprint", changed))
                .isInstanceOf(BusinessException.class);
        assertThat(inventory.findById(productId).orElseThrow().getReserved()).isEqualTo(1);
    }

    @Test
    void concurrentSameKeyCreatesOneOrder() throws Exception {
        try (var pool = java.util.concurrent.Executors.newFixedThreadPool(2)) {
            var start = new java.util.concurrent.CountDownLatch(1);
            java.util.concurrent.Callable<UUID> action =
                    () -> {
                        start.await();
                        return create("concurrent").id();
                    };
            var a = pool.submit(action);
            var b = pool.submit(action);
            start.countDown();
            assertThat(a.get(10, java.util.concurrent.TimeUnit.SECONDS))
                    .isEqualTo(b.get(10, java.util.concurrent.TimeUnit.SECONDS));
        }
        assertThat(inventory.findById(productId).orElseThrow().getReserved()).isEqualTo(1);
    }

    @Test
    void cancelledOrderReleasesStockOnlyOnce() {
        var order = create("cancel-once");
        commands.cancel(order.id(), buyer);
        commands.cancel(order.id(), buyer);
        assertThat(inventory.findById(productId).orElseThrow().getAvailable()).isEqualTo(10);
        assertThat(inventory.findById(productId).orElseThrow().getReserved()).isZero();
    }

    @Test
    void unknownPaymentCannotBeRetriedWithANewKeyOrCancelled() {
        var order = create("unknown-order");
        var first = paymentFlow.pay(order.id(), buyer, "unknown-key", "timeout");
        assertThat(first.status()).isEqualTo("UNKNOWN");
        assertThat(paymentFlow.pay(order.id(), buyer, "unknown-key", "timeout").paymentId())
                .isEqualTo(first.paymentId());
        assertThatThrownBy(() -> paymentFlow.pay(order.id(), buyer, "new-key", "success"))
                .isInstanceOf(BusinessException.class);
        assertThatThrownBy(() -> commands.cancel(order.id(), buyer))
                .isInstanceOf(BusinessException.class);
    }

    @Test
    void declinedPaymentAllowsCancellation() {
        var order = create("decline-order");
        assertThat(paymentFlow.pay(order.id(), buyer, "decline-key", "decline").status())
                .isEqualTo("DECLINED");
        assertThat(commands.cancel(order.id(), buyer).status()).isEqualTo("CANCELLED");
    }

    @Test
    void refundReplayStillChecksOwnership() {
        var order = create("private-refund");
        var payment = paymentFlow.pay(order.id(), buyer, "private-payment", "success");
        refunds.refund(payment.paymentId(), buyer, "private-key");
        var other =
                users.save(
                        new UserEntity(
                                UUID.randomUUID() + "@example.com",
                                "other",
                                "hash",
                                UserRole.USER));
        assertThatThrownBy(
                        () ->
                                refunds.refund(
                                        payment.paymentId(),
                                        UserPrincipal.from(other),
                                        "private-key"))
                .isInstanceOf(BusinessException.class);
    }

    @Test
    void duplicateConsumersDoNotDuplicateSideEffects() throws Exception {
        var order = create("message-order");
        paymentFlow.pay(order.id(), buyer, "message-pay", "success");
        String payload =
                jdbc.queryForObject(
                        "select payload from outbox_events where aggregate_id=? and event_type='order.paid.v1'",
                        String.class,
                        order.id().toString());
        consumers.notifyUser(payload);
        consumers.notifyUser(payload);
        consumers.addPoints(payload);
        consumers.addPoints(payload);
        assertThat(
                        jdbc.queryForObject(
                                "select count(*) from notifications where user_id=?",
                                Integer.class,
                                buyer.id()))
                .isEqualTo(1);
        assertThat(
                        jdbc.queryForObject(
                                "select count(*) from points_ledger where order_id=?",
                                Integer.class,
                                order.id()))
                .isEqualTo(1);
        assertThat(
                        jdbc.queryForObject(
                                "select points from points_ledger where order_id=?",
                                Long.class,
                                order.id()))
                .isEqualTo(2L);
    }

    @Test
    void failedConsumerRollsBackDedupMarker() throws Exception {
        UUID eventId = UUID.randomUUID();
        var bad =
                new com.example.minicommerce.messaging.application.EventEnvelope(
                        eventId,
                        "order.paid.v1",
                        1,
                        java.time.Instant.now(),
                        "test",
                        "ORDER",
                        UUID.randomUUID().toString(),
                        null,
                        json.createObjectNode());
        String raw = json.writeValueAsString(bad);
        assertThatThrownBy(() -> consumers.notifyUser(raw)).isInstanceOf(Exception.class);
        assertThat(
                        jdbc.queryForObject(
                                "select count(*) from processed_messages where event_id=?",
                                Integer.class,
                                eventId))
                .isZero();
    }

    @Test
    void staleOutboxWorkerCannotOverwriteNewLease() {
        var order = create("lease-order");
        UUID eventId =
                jdbc.queryForObject(
                        "select event_id from outbox_events where aggregate_id=?",
                        UUID.class,
                        order.id().toString());
        var a =
                outboxJobs.claim("worker-a", 1000, java.time.Duration.ofSeconds(30)).stream()
                        .filter(e -> e.eventId().equals(eventId))
                        .findFirst()
                        .orElseThrow();
        jdbc.update(
                "update outbox_events set locked_until=now()-interval '1 second' where event_id=?",
                eventId);
        var b =
                outboxJobs.claim("worker-b", 1000, java.time.Duration.ofSeconds(30)).stream()
                        .filter(e -> e.eventId().equals(eventId))
                        .findFirst()
                        .orElseThrow();
        assertThat(outboxJobs.published(eventId, "worker-a", a.attemptCount())).isFalse();
        outboxJobs.failed(eventId, "worker-a", a.attemptCount(), "late failure");
        assertThat(outboxJobs.published(eventId, "worker-b", b.attemptCount())).isTrue();
    }

    @Test
    void refreshTokenCanOnlyBeRotatedOnceConcurrently() throws Exception {
        var account =
                authentication.register(
                        new com.example.minicommerce.identity.api.AuthDtos.RegisterRequest(
                                UUID.randomUUID() + "@example.com",
                                "refresh user",
                                "LongPassword123!"));
        var request =
                new com.example.minicommerce.identity.api.AuthDtos.RefreshRequest(
                        account.refreshToken());
        try (var pool = java.util.concurrent.Executors.newFixedThreadPool(2)) {
            var start = new java.util.concurrent.CountDownLatch(1);
            java.util.concurrent.Callable<Boolean> action =
                    () -> {
                        start.await();
                        try {
                            authentication.refresh(request);
                            return true;
                        } catch (BusinessException rejected) {
                            return false;
                        }
                    };
            var a = pool.submit(action);
            var b = pool.submit(action);
            start.countDown();
            assertThat(
                            List.of(
                                    a.get(10, java.util.concurrent.TimeUnit.SECONDS),
                                    b.get(10, java.util.concurrent.TimeUnit.SECONDS)))
                    .containsExactlyInAnyOrder(true, false);
        }
    }

    @Test
    void bcryptByteLimitIsAValidationError() {
        var request =
                new com.example.minicommerce.identity.api.AuthDtos.RegisterRequest(
                        UUID.randomUUID() + "@example.com", "name", "密".repeat(25));
        assertThatThrownBy(() -> authentication.register(request))
                .isInstanceOf(BusinessException.class);
    }

    @Test
    void protectedApiAndManagementRoutesEnforcePermissions() throws Exception {
        var order = create("access-order");
        var other =
                users.save(
                        new UserEntity(
                                UUID.randomUUID() + "@example.com",
                                "other",
                                "hash",
                                UserRole.USER));
        http.perform(get("/api/orders/" + order.id())).andExpect(status().isUnauthorized());
        http.perform(get("/api/orders/" + order.id()).with(user(UserPrincipal.from(other))))
                .andExpect(status().isForbidden());
        http.perform(get("/actuator/metrics").with(user(buyer))).andExpect(status().isForbidden());
        http.perform(put("/api/orders/" + order.id()).with(user(buyer)))
                .andExpect(status().isMethodNotAllowed());
    }
}
