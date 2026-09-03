package com.example.minicommerce.notification.infrastructure;

import jakarta.persistence.*;
import java.time.Instant;
import java.util.UUID;

/**
 * 通知模块的基础设施适配层：{@code PointsLedgerEntity}。
 *
 * <p><strong>作用：</strong>负责 JPA、SQL、Redis、RabbitMQ 或外部系统等技术实现，并把技术细节隔离在业务边界之外。
 *
 * <p><strong>为什么：</strong>数据库表和框架会变化；隔离适配器可以避免这些变化扩散到业务规则和 API 契约。
 *
 * <p><strong>对应文档：</strong> {@code 07_rabbitmq/01_同步异步与事件边界.md}、 {@code
 * 07_rabbitmq/04_幂等与Outbox.md}。
 */
@Entity
@Table(
        name = "points_ledger",
        uniqueConstraints =
                @UniqueConstraint(
                        name = "ux_points_order_reason",
                        columnNames = {"order_id", "reason"}))
public class PointsLedgerEntity {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "user_id", nullable = false)
    private Long userId;

    @Column(name = "order_id", nullable = false)
    private UUID orderId;

    @Column(nullable = false, length = 50)
    private String reason;

    @Column(nullable = false)
    private int points;

    @Column(name = "created_at", nullable = false)
    private Instant createdAt;

    protected PointsLedgerEntity() {}

    public PointsLedgerEntity(Long u, UUID o, int p, Instant n) {
        userId = u;
        orderId = o;
        reason = "ORDER_PAID";
        points = p;
        createdAt = n;
    }
}
