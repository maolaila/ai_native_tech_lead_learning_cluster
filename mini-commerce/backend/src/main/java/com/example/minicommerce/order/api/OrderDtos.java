package com.example.minicommerce.order.api;

import jakarta.validation.Valid;
import jakarta.validation.constraints.*;
import java.math.BigDecimal;
import java.time.Instant;
import java.util.*;

/**
 * 规定下单请求和订单响应的字段。
 *
 * <p><strong>作用：</strong>规定下单请求和订单响应的字段。
 *
 * <p><strong>为什么：</strong>请求只接收商品、数量和优惠券，不接收用户 ID 或最终价格。响应包含后端算出的金额和成交快照。
 *
 * <p><strong>对应文档：</strong> {@code 02_backend_spring/06_订单模块案例.md}、 {@code
 * 04_database_postgresql/04_事务与Spring边界.md}、 {@code 07_rabbitmq/04_幂等与Outbox.md}。
 */
public final class OrderDtos {
    private OrderDtos() {}

    public record CreateOrderRequest(
            @NotEmpty @Size(max = 50) List<@NotNull @Valid OrderLineRequest> items,
            @Size(max = 50) String couponCode) {}

    public record OrderLineRequest(@NotNull @Positive Long productId, @Positive int quantity) {}

    public record OrderResponse(
            UUID id,
            String orderNumber,
            Long userId,
            String status,
            BigDecimal subtotal,
            BigDecimal discount,
            BigDecimal totalAmount,
            String currency,
            List<OrderLineResponse> items,
            Instant createdAt) {}

    public record OrderLineResponse(
            Long productId,
            String productName,
            String sku,
            BigDecimal unitPrice,
            int quantity,
            BigDecimal lineTotal) {}
}
