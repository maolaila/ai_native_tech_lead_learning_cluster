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
 * 查订单、组装明细，并判断当前用户能否读取或修改该订单。
 *
 * <p><strong>作用：</strong>查订单、组装明细，并判断当前用户能否读取或修改该订单。
 *
 * <p><strong>为什么：</strong>“能查别人的订单”和“能修改别人的订单”是两种权限；客服读权限不能直接复用成写权限。
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

    /** 能查看不等于能修改；客服可协助查询，但不可替别人取消订单。 */
    public void authorizeWrite(OrderEntity order, UserPrincipal actor) {
        if (!order.getUserId().equals(actor.id()) && !actor.role().name().equals("ADMIN")) {
            throw new BusinessException(ErrorCode.ACCESS_DENIED, "没有修改该订单的权限");
        }
    }
}
