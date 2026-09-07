package com.example.minicommerce.order.infrastructure;

import jakarta.persistence.*;
import java.time.Instant;
import java.util.UUID;

/**
 * 订单模块的基础设施适配层：{@code IdempotencyRecordEntity}。
 *
 * <p><strong>作用：</strong>把数据库 idempotency_records 表的一条记录映射成 Java 对象，并保存本实体的状态。这个类不负责 Redis 或
 * RabbitMQ 通信。
 *
 * <p><strong>为什么：</strong>数据库表和框架会变化；隔离适配器可以避免这些变化扩散到业务规则和 API 契约。
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
