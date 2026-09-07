package com.example.minicommerce;

import static org.assertj.core.api.Assertions.*;
import static org.springframework.security.test.web.servlet.request.SecurityMockMvcRequestPostProcessors.user;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;
import static org.mockito.ArgumentMatchers.*;
import static org.mockito.Mockito.when;

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
import org.springframework.test.context.bean.override.mockito.MockitoBean;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.test.web.servlet.MockMvc;

/**
 * 开学前回归测试：断言数据库里的最终事实，而不只断言方法返回值。
 * 对应文档：mini-commerce/docs/testing-strategy.md。
 * 不给测试方法加事务，防止测试自身的事务掩盖业务入口缺少事务的问题。
 */
@AutoConfigureMockMvc
class LearningReadinessIT extends AbstractPostgresIT {
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
    UserPrincipal buyer;
    Long productId;

    @BeforeEach
    void prepareIndependentData() {
        var account = users.save(new UserEntity(UUID.randomUUID() + "@example.com", "buyer", "hash", UserRole.USER));
        buyer = UserPrincipal.from(account);
        var product = new ProductEntity("SKU-" + UUID.randomUUID(), "验收商品", "test", new BigDecimal("200.00"), "CNY");
        product.publish();
        product = products.saveAndFlush(product);
        productId = product.getId();
        inventory.saveAndFlush(new InventoryEntity(productId, 10));
        // 本组只检查 HTTP 契约；真实 Redis 与限流在 Compose/独立测试中验证。
        when(rateLimits.allow(anyString(), anyInt(), any(), anyBoolean())).thenReturn(true);
    }

    private OrderResponse create(String key) {
        return createOrders.create(buyer.id(), key, new CreateOrderRequest(List.of(new OrderLineRequest(productId, 1)), null));
    }

    @Test
    void repeatedOrderReturnsSameOrderAndDoesNotReserveStockTwice() {
        var first = create("same-order-key");
        assertThat(jdbc.queryForObject("select status from idempotency_records where user_id=? and idempotency_key=?", String.class, buyer.id(), "same-order-key"))
                .isEqualTo("COMPLETED");
        assertThat(create("same-order-key").id()).isEqualTo(first.id());
        assertThat(inventory.findById(productId).orElseThrow().getReserved()).isEqualTo(1);
    }

    @Test
    void successfulPaymentIsPersistedAndCanBeReplayed() {
        var order = create("pay-order");
        var payment = paymentFlow.pay(order.id(), buyer, "payment-key", "success");
        assertThat(jdbc.queryForObject("select status from payment_attempts where id=?", String.class, payment.paymentId())).isEqualTo("SUCCEEDED");
        assertThat(jdbc.queryForObject("select status from orders where id=?", String.class, order.id())).isEqualTo("PAID");
        assertThat(paymentFlow.pay(order.id(), buyer, "payment-key", "success").paymentId()).isEqualTo(payment.paymentId());
        assertThat(inventory.findById(productId).orElseThrow().getReserved()).isZero();
    }

    @Test
    void oneOrderCannotStartTwoUnresolvedPayments() {
        var order = create("pending-pay-order");
        paymentTransactions.createOrGet(order.id(), buyer, "first-payment", "success");
        assertThatThrownBy(() -> paymentTransactions.createOrGet(order.id(), buyer, "second-payment", "success"))
                .isInstanceOf(BusinessException.class);
    }

    @Test
    void cancellationCannotRaceWithAnUnresolvedPayment() {
        var order = create("cancel-pay-order");
        paymentTransactions.createOrGet(order.id(), buyer, "pending-payment", "success");
        assertThatThrownBy(() -> commands.cancel(order.id(), buyer)).isInstanceOf(BusinessException.class);
        assertThat(inventory.findById(productId).orElseThrow().getReserved()).isEqualTo(1);
    }

    @Test
    void refundPublicEntryUsesRealTransactions() {
        var order = create("refund-order");
        var payment = paymentFlow.pay(order.id(), buyer, "refund-payment", "success");
        var refund = refunds.refund(payment.paymentId(), buyer, "refund-key");
        assertThat(refund.status()).isEqualTo("SUCCEEDED");
        assertThat(jdbc.queryForObject("select status from orders where id=?", String.class, order.id())).isEqualTo("REFUNDED");
        assertThat(refunds.refund(payment.paymentId(), buyer, "refund-key").refundId()).isEqualTo(refund.refundId());
    }

    @Test
    void requestErrorsAreClientErrorsNotInternalErrors() throws Exception {
        http.perform(post("/api/orders").with(user(buyer)).contentType("application/json")
                .content("{\"items\":[{\"productId\":" + productId + ",\"quantity\":1}]}"))
                .andExpect(status().isBadRequest()).andExpect(jsonPath("$.code").value("VALIDATION_ERROR"));
        http.perform(post("/api/orders").with(user(buyer)).header("Idempotency-Key", "bad-json")
                .contentType("application/json").content("{"))
                .andExpect(status().isBadRequest());
        http.perform(get("/api/orders/not-a-uuid").with(user(buyer)))
                .andExpect(status().isBadRequest());
    }

    @Test
    void quantityOverflowIsRejectedAsValidationFailure() {
        var request = new CreateOrderRequest(List.of(new OrderLineRequest(productId, Integer.MAX_VALUE), new OrderLineRequest(productId, 1)), null);
        assertThatThrownBy(() -> createOrders.create(buyer.id(), "overflow", request)).isInstanceOf(BusinessException.class);
    }
}
