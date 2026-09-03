package com.example.minicommerce.order.api;

import jakarta.validation.Valid;
import jakarta.validation.constraints.*;
import java.math.BigDecimal;
import java.time.Instant;
import java.util.*;

/**
 * 订单模块的HTTP/API 适配层：{@code OrderDtos}。
 *
 * <p><strong>作用：</strong>负责路由、请求参数、校验、认证主体和 HTTP 响应转换，不承载核心业务规则。
 *
 * <p><strong>为什么：</strong>把 HTTP 细节留在系统边界，应用服务才能脱离 Web 框架测试和复用。
 *
 * <p><strong>对应文档：</strong> {@code 02_backend_spring/06_订单模块案例.md}、 {@code
 * 04_database_postgresql/04_事务与Spring边界.md}、 {@code 07_rabbitmq/04_幂等与Outbox.md}。
 */
public final class OrderDtos {
    private OrderDtos() {}

    public record CreateOrderRequest(
            @NotEmpty @Size(max = 50) List<@Valid OrderLineRequest> items,
            @Size(max = 50) String couponCode) {}

    public record OrderLineRequest(@NotNull Long productId, @Positive int quantity) {}

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
