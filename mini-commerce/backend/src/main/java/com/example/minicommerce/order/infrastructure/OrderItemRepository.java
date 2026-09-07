package com.example.minicommerce.order.infrastructure;

import java.util.*;
import org.springframework.data.jpa.repository.JpaRepository;

/**
 * 按订单 ID 取出成交明细，并按明细 ID 返回稳定顺序。
 *
 * <p><strong>作用：</strong>按订单 ID 取出成交明细，并按明细 ID 返回稳定顺序。
 *
 * <p><strong>为什么：</strong>这些明细保存历史快照，不应在读历史订单时重新拿商品当前价格计算金额。
 *
 * <p><strong>对应文档：</strong> {@code 02_backend_spring/06_订单模块案例.md}、 {@code
 * 04_database_postgresql/04_事务与Spring边界.md}、 {@code 07_rabbitmq/04_幂等与Outbox.md}。
 */
public interface OrderItemRepository extends JpaRepository<OrderItemEntity, UUID> {
    List<OrderItemEntity> findByOrderIdOrderById(UUID orderId);
}
