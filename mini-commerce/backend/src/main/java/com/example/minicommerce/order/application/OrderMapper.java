package com.example.minicommerce.order.application;

import static com.example.minicommerce.order.api.OrderDtos.*;

import com.example.minicommerce.order.infrastructure.*;
import java.util.*;

/**
 * 把订单主记录和成交明细转换成接口响应。
 *
 * <p><strong>作用：</strong>把订单主记录和成交明细转换成接口响应。
 *
 * <p><strong>为什么：</strong>转换对象不应再查数据库或重新计价；这样历史订单返回的金额来自保存的成交事实。
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
