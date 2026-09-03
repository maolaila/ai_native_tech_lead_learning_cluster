package com.example.minicommerce.order.domain;

import static org.assertj.core.api.Assertions.*;

import com.example.minicommerce.order.infrastructure.OrderEntity;
import com.example.minicommerce.shared.error.BusinessException;
import java.math.BigDecimal;
import java.time.Instant;
import java.util.UUID;
import org.junit.jupiter.api.Test;

/**
 * 订单模块的自动化验证层：{@code OrderEntityTest}。
 *
 * <p><strong>作用：</strong>提供可重复的行为、数据、并发或故障证据，而不是只证明代码能够编译。
 *
 * <p><strong>为什么：</strong>历史规则和 Bug 只有进入自动化测试，才不会在后续重构或 AI 生成代码时悄悄回归。
 *
 * <p><strong>对应文档：</strong> {@code 02_backend_spring/06_订单模块案例.md}、 {@code
 * 04_database_postgresql/04_事务与Spring边界.md}、 {@code 07_rabbitmq/04_幂等与Outbox.md}。
 */
class OrderEntityTest {
    private OrderEntity order(String n) {
        return new OrderEntity(
                UUID.randomUUID(),
                n,
                1L,
                new BigDecimal("100"),
                BigDecimal.ZERO,
                new BigDecimal("100"),
                "JPY",
                null,
                Instant.parse("2026-01-01T00:00:00Z"));
    }

    @Test
    void cancelledOrder_cannotBePaid() {
        OrderEntity o = order("MC-X");
        o.cancel(Instant.parse("2026-01-01T00:00:01Z"));
        assertThatThrownBy(() -> o.markPaid(UUID.randomUUID(), Instant.now()))
                .isInstanceOf(BusinessException.class);
    }

    @Test
    void duplicateCancel_reportsNoSecondSideEffect() {
        OrderEntity o = order("MC-Y");
        assertThat(o.cancel(Instant.now())).isTrue();
        assertThat(o.cancel(Instant.now())).isFalse();
        assertThat(o.getStatus()).isEqualTo(OrderStatus.CANCELLED);
    }

    @Test
    void refundFailure_returnsPaidForSafeRetry() {
        OrderEntity o = order("MC-Z");
        o.markPaid(UUID.randomUUID(), Instant.now());
        o.requestRefund(Instant.now());
        o.refundFailed(Instant.now());
        assertThat(o.getStatus()).isEqualTo(OrderStatus.PAID);
    }
}
