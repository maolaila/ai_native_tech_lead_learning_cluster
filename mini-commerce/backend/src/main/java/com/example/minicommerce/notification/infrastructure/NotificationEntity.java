package com.example.minicommerce.notification.infrastructure;

import jakarta.persistence.*;
import java.time.Instant;
import java.util.UUID;

/**
 * 保存一条发给某个用户的站内通知，包括内容、未读标志和创建时间。
 *
 * <p><strong>作用：</strong>保存一条发给某个用户的站内通知，包括内容、未读标志和创建时间。
 *
 * <p><strong>为什么：</strong>这里的通知是一条数据库记录，不是已经发送的短信或邮件；当前项目没有实现短信发送或标记已读接口。
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
