package com.example.minicommerce.order.application;

import static com.example.minicommerce.order.api.OrderDtos.*;

import com.example.minicommerce.audit.application.AuditService;
import com.example.minicommerce.inventory.application.InventoryService;
import com.example.minicommerce.messaging.application.OutboxService;
import com.example.minicommerce.order.infrastructure.*;
import com.example.minicommerce.promotion.application.CouponService;
import com.example.minicommerce.shared.error.*;
import com.example.minicommerce.shared.security.UserPrincipal;
import java.time.Clock;
import java.util.*;
import java.util.stream.Collectors;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

/**
 * 订单模块的应用用例编排层：{@code OrderCommandService}。
 *
 * <p><strong>作用：</strong>编排一个完整业务用例，协调领域规则、仓储、外部端口与事务边界。
 *
 * <p><strong>为什么：</strong>事务应该围绕业务动作，而不是分散在 Controller 或每个 Repository 中。
 *
 * <p><strong>对应文档：</strong> {@code 02_backend_spring/06_订单模块案例.md}、 {@code
 * 04_database_postgresql/04_事务与Spring边界.md}、 {@code 07_rabbitmq/04_幂等与Outbox.md}。
 */
@Service
public class OrderCommandService {
    private final OrderRepository orders;
    private final OrderItemRepository items;
    private final InventoryService inventory;
    private final CouponService coupons;
    private final OutboxService outbox;
    private final OrderQueryService query;
    private final AuditService audit;
    private final Clock clock;

    public OrderCommandService(
            OrderRepository o,
            OrderItemRepository i,
            InventoryService inv,
            CouponService c,
            OutboxService out,
            OrderQueryService q,
            AuditService a,
            Clock clock) {
        orders = o;
        items = i;
        inventory = inv;
        coupons = c;
        outbox = out;
        query = q;
        audit = a;
        this.clock = clock;
    }

    @Transactional
    public OrderResponse cancel(UUID id, UserPrincipal actor) {
        OrderEntity order =
                orders.findForUpdate(id)
                        .orElseThrow(
                                () -> new BusinessException(ErrorCode.ORDER_NOT_FOUND, "订单不存在"));
        query.authorize(order, actor);
        List<OrderItemEntity> lines = items.findByOrderIdOrderById(id);
        String before = order.getStatus().name();
        if (!order.cancel(clock.instant())) return OrderMapper.view(order, lines);
        Map<Long, Integer> qty =
                lines.stream()
                        .collect(
                                Collectors.toMap(
                                        OrderItemEntity::getProductId,
                                        OrderItemEntity::getQuantity));
        inventory.release(qty);
        coupons.release(order.getUserCouponId(), id);
        outbox.append(
                "ORDER",
                id.toString(),
                "order.cancelled.v1",
                Map.of("orderId", id, "userId", order.getUserId()));
        audit.record(
                actor.id(),
                "ORDER_CANCEL",
                "ORDER",
                id,
                Map.of("status", before),
                Map.of("status", order.getStatus()));
        return OrderMapper.view(order, lines);
    }
}
