package com.example.minicommerce.order.infrastructure;

import java.util.*;
import org.springframework.data.jpa.repository.JpaRepository;

/**
 * 订单模块的基础设施适配层：{@code OrderItemRepository}。
 *
 * <p><strong>作用：</strong>声明数据库查询或更新能力，由 Spring Data 创建实现；它不负责 Redis、RabbitMQ，也不决定整个业务流程。
 *
 * <p><strong>为什么：</strong>数据库表和框架会变化；隔离适配器可以避免这些变化扩散到业务规则和 API 契约。
 *
 * <p><strong>对应文档：</strong> {@code 02_backend_spring/06_订单模块案例.md}、 {@code
 * 04_database_postgresql/04_事务与Spring边界.md}、 {@code 07_rabbitmq/04_幂等与Outbox.md}。
 */
public interface OrderItemRepository extends JpaRepository<OrderItemEntity, UUID> {
    List<OrderItemEntity> findByOrderIdOrderById(UUID orderId);
}
