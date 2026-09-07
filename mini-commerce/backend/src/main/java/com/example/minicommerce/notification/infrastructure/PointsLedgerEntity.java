package com.example.minicommerce.notification.infrastructure;

import jakarta.persistence.*;
import java.time.Instant;
import java.util.UUID;

/**
 * 保存一笔订单付款后增加的积分明细。
 *
 * <p><strong>作用：</strong>保存一笔订单付款后增加的积分明细。
 *
 * <p><strong>为什么：</strong>orderId 与 reason 的组合只能出现一次，作为重复消费的第二道防线。points 使用 long；当前退款流程还没有冲回积分。
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
    private long points;

    @Column(name = "created_at", nullable = false)
    private Instant createdAt;

    protected PointsLedgerEntity() {}

    public PointsLedgerEntity(Long u, UUID o, long p, Instant n) {
        userId = u;
        orderId = o;
        reason = "ORDER_PAID";
        points = p;
        createdAt = n;
    }
}
