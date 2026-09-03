package com.example.minicommerce.order.domain;

/**
 * 订单模块的领域模型层：{@code OrderStatus}。
 *
 * <p><strong>作用：</strong>表达业务状态、行为和不变量，并尽量保持对 Spring、HTTP 与数据库实现无感。
 *
 * <p><strong>为什么：</strong>领域方法比任意 Setter 更能阻止非法状态，也使测试直接描述业务语言。
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
