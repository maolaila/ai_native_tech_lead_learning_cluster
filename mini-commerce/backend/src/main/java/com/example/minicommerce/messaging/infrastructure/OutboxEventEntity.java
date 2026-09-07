package com.example.minicommerce.messaging.infrastructure;

import jakarta.persistence.*;
import java.time.Instant;
import java.util.UUID;

/**
 * 保存一封待寄的业务消息：事件编号、类型、内容、重试次数和领取人。
 *
 * <p><strong>作用：</strong>保存一封待寄的业务消息：事件编号、类型、内容、重试次数和领取人。
 *
 * <p><strong>为什么：</strong>事件先留在数据库里，程序重启后还可继续发送。PUBLISHED 只说明发布成功，不代表下游业务已经处理成功。
 *
 * <p><strong>对应文档：</strong> {@code 07_rabbitmq/02_Exchange_Queue_Routing.md}、 {@code
 * 07_rabbitmq/03_Confirm_Ack_Retry_DLQ.md}、 {@code 07_rabbitmq/04_幂等与Outbox.md}。
 */
@Entity
@Table(
        name = "outbox_events",
        indexes =
                @Index(
                        name = "ix_outbox_pending",
                        columnList = "status,next_attempt_at,created_at"))
public class OutboxEventEntity {
    @Id
    @Column(name = "event_id")
    private UUID eventId;

    @Column(name = "aggregate_type", nullable = false, length = 80)
    private String aggregateType;

    @Column(name = "aggregate_id", nullable = false, length = 100)
    private String aggregateId;

    @Column(name = "event_type", nullable = false, length = 100)
    private String eventType;

    @Column(name = "schema_version", nullable = false)
    private int schemaVersion;

    @Column(nullable = false, columnDefinition = "text")
    private String payload;

    @Column(nullable = false, length = 20)
    private String status;

    @Column(name = "attempt_count", nullable = false)
    private int attemptCount;

    @Column(name = "next_attempt_at", nullable = false)
    private Instant nextAttemptAt;

    @Column(name = "locked_by", length = 100)
    private String lockedBy;

    @Column(name = "locked_until")
    private Instant lockedUntil;

    @Column(name = "last_error", length = 1000)
    private String lastError;

    @Column(name = "created_at", nullable = false)
    private Instant createdAt;

    @Column(name = "published_at")
    private Instant publishedAt;

    protected OutboxEventEntity() {}

    public OutboxEventEntity(
            UUID id, String at, String ai, String et, String payload, Instant now) {
        eventId = id;
        aggregateType = at;
        aggregateId = ai;
        eventType = et;
        schemaVersion = 1;
        this.payload = payload;
        status = "PENDING";
        nextAttemptAt = now;
        createdAt = now;
    }

    public UUID getEventId() {
        return eventId;
    }
}
