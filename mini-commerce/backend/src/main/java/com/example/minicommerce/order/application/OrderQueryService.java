package com.example.minicommerce.order.application;

import static com.example.minicommerce.order.api.OrderDtos.*;

import com.example.minicommerce.order.infrastructure.*;
import com.example.minicommerce.shared.error.*;
import com.example.minicommerce.shared.security.UserPrincipal;
import java.util.*;
import org.springframework.data.domain.*;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

/**
 * 订单模块的应用用例编排层：{@code OrderQueryService}。
 *
 * <p><strong>作用：</strong>编排一个完整业务用例，协调领域规则、仓储、外部端口与事务边界。
 *
 * <p><strong>为什么：</strong>事务应该围绕业务动作，而不是分散在 Controller 或每个 Repository 中。
 *
 * <p><strong>对应文档：</strong> {@code 02_backend_spring/06_订单模块案例.md}、 {@code
 * 04_database_postgresql/04_事务与Spring边界.md}、 {@code 07_rabbitmq/04_幂等与Outbox.md}。
 */
@Service
public class OrderQueryService {
    private final OrderRepository orders;
    private final OrderItemRepository items;

    public OrderQueryService(OrderRepository o, OrderItemRepository i) {
        orders = o;
        items = i;
    }

    @Transactional(readOnly = true)
    public OrderResponse get(UUID id, UserPrincipal actor) {
        OrderEntity o =
                orders.findById(id)
                        .orElseThrow(
                                () -> new BusinessException(ErrorCode.ORDER_NOT_FOUND, "订单不存在"));
        authorize(o, actor);
        return view(o);
    }

    @Transactional(readOnly = true)
    public Page<OrderResponse> list(UserPrincipal actor, Pageable p) {
        Page<OrderEntity> page =
                actor.role().name().equals("ADMIN")
                        ? orders.findAll(p)
                        : orders.findByUserId(actor.id(), p);
        return page.map(this::view);
    }

    public OrderResponse view(OrderEntity o) {
        return OrderMapper.view(o, items.findByOrderIdOrderById(o.getId()));
    }

    public void authorize(OrderEntity o, UserPrincipal a) {
        if (!o.getUserId().equals(a.id())
                && !a.role().name().equals("ADMIN")
                && !a.role().name().equals("SUPPORT"))
            throw new BusinessException(ErrorCode.ACCESS_DENIED, "不能访问他人的订单");
    }
}
