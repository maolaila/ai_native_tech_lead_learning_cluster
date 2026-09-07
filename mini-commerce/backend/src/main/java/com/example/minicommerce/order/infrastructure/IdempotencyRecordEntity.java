package com.example.minicommerce.order.infrastructure;

import jakarta.persistence.*;
import java.time.Instant;
import java.util.UUID;

/**
 * 保存下单幂等键、请求指纹、处理状态和最终订单 ID。
 *
 * <p><strong>作用：</strong>保存下单幂等键、请求指纹、处理状态和最终订单 ID。
 *
 * <p><strong>为什么：</strong>相同键重试复用原订单；相同键却更换商品必须拒绝。expiresAt 只是数据字段，当前没有自动清理或到期复用任务。
 *
 * <p><strong>对应文档：</strong> {@code 02_backend_spring/06_订单模块案例.md}、 {@code
 * 04_database_postgresql/04_事务与Spring边界.md}、 {@code 07_rabbitmq/04_幂等与Outbox.md}。
 */
@Entity
@Table(
        name = "idempotency_records",
        uniqueConstraints =
                @UniqueConstraint(
                        name = "ux_idempotency_user_key",
                        columnNames = {"user_id", "idempotency_key"}))
public class IdempotencyRecordEntity {
    @Id private UUID id;

    @Column(name = "user_id", nullable = false)
    private Long userId;

    @Column(name = "idempotency_key", nullable = false, length = 128)
    private String key;

    @Column(name = "request_hash", nullable = false, length = 64)
    private String requestHash;

    @Column(nullable = false, length = 20)
    private String status;

    @Column(name = "resource_id")
    private UUID resourceId;

    @Column(name = "created_at", nullable = false)
    private Instant createdAt;

    @Column(name = "expires_at", nullable = false)
    private Instant expiresAt;

    protected IdempotencyRecordEntity() {}

    public IdempotencyRecordEntity(Long u, String k, String h, Instant now) {
        id = UUID.randomUUID();
        userId = u;
        key = k;
        requestHash = h;
        status = "PROCESSING";
        createdAt = now;
        expiresAt = now.plusSeconds(86400);
    }

    public String getRequestHash() {
        return requestHash;
    }

    public String getStatus() {
        return status;
    }

    public UUID getResourceId() {
        return resourceId;
    }

    public void complete(UUID id) {
        resourceId = id;
        status = "COMPLETED";
    }
}
