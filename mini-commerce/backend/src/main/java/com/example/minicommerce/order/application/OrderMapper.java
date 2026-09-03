package com.example.minicommerce.order.application;

import static com.example.minicommerce.order.api.OrderDtos.*;

import com.example.minicommerce.order.infrastructure.*;
import java.util.*;

/**
 * 订单模块的应用用例编排层：{@code OrderMapper}。
 *
 * <p><strong>作用：</strong>编排一个完整业务用例，协调领域规则、仓储、外部端口与事务边界。
 *
 * <p><strong>为什么：</strong>事务应该围绕业务动作，而不是分散在 Controller 或每个 Repository 中。
 *
 * <p><strong>对应文档：</strong> {@code 02_backend_spring/06_订单模块案例.md}、 {@code
 * 04_database_postgresql/04_事务与Spring边界.md}、 {@code 07_rabbitmq/04_幂等与Outbox.md}。
 */
public final class OrderMapper {
    private OrderMapper() {}

    public static OrderResponse view(OrderEntity o, List<OrderItemEntity> items) {
        return new OrderResponse(
                o.getId(),
                o.getOrderNumber(),
                o.getUserId(),
                o.getStatus().name(),
                o.getSubtotal(),
                o.getDiscount(),
                o.getTotalAmount(),
                o.getCurrency(),
                items.stream()
                        .map(
                                i ->
                                        new OrderLineResponse(
                                                i.getProductId(),
                                                i.getProductName(),
                                                i.getSku(),
                                                i.getUnitPrice(),
                                                i.getQuantity(),
                                                i.getLineTotal()))
                        .toList(),
                o.getCreatedAt());
    }
}
