package com.example.minicommerce.notification.infrastructure;

import jakarta.persistence.*;
import java.time.Instant;
import java.util.UUID;

/**
 * 通知模块的基础设施适配层：{@code NotificationEntity}。
 *
 * <p><strong>作用：</strong>把数据库 notifications 表的一条记录映射成 Java 对象，并保存本实体的状态。这个类不负责 Redis 或 RabbitMQ 通信。
 *
 * <p><strong>为什么：</strong>数据库表和框架会变化；隔离适配器可以避免这些变化扩散到业务规则和 API 契约。
 *
 * <p><strong>对应文档：</strong> {@code 07_rabbitmq/01_同步异步与事件边界.md}、 {@code
 * 07_rabbitmq/04_幂等与Outbox.md}。
 */
@Entity
@Table(name = "notifications")
public class NotificationEntity {
    @Id private UUID id;

    @Column(name = "user_id", nullable = false)
    private Long userId;

    @Column(nullable = false, length = 100)
    private String type;

    @Column(nullable = false, length = 500)
    private String message;

    @Column(nullable = false)
    private boolean unread;

    @Column(name = "created_at", nullable = false)
    private Instant createdAt;

    protected NotificationEntity() {}

    public NotificationEntity(Long u, String t, String m, Instant n) {
        id = UUID.randomUUID();
        userId = u;
        type = t;
        message = m;
        unread = true;
        createdAt = n;
    }

    public UUID getId() {
        return id;
    }

    public Long getUserId() {
        return userId;
    }

    public String getMessage() {
        return message;
    }

    public boolean isUnread() {
        return unread;
    }

    public Instant getCreatedAt() {
        return createdAt;
    }
}
