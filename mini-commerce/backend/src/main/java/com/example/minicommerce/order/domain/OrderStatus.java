package com.example.minicommerce.order.domain;

/**
 * 列出订单允许使用的状态名称。
 *
 * <p><strong>作用：</strong>列出订单允许使用的状态名称。
 *
 * <p><strong>为什么：</strong>枚举不会自己执行状态变化；要读 OrderEntity 的动作方法。FULFILLING 和 COMPLETED
 * 是预留状态，当前没有完整发货接口。
 *
 * <p><strong>对应文档：</strong> {@code 02_backend_spring/06_订单模块案例.md}、 {@code
 * 04_database_postgresql/04_事务与Spring边界.md}、 {@code 07_rabbitmq/04_幂等与Outbox.md}。
 */
public enum OrderStatus {
    PENDING_PAYMENT,
    PAID,
    FULFILLING,
    COMPLETED,
    CANCELLED,
    REFUNDING,
    REFUNDED
}
