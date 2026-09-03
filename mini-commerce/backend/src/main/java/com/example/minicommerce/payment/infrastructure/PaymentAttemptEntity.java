package com.example.minicommerce.payment.infrastructure;

import com.example.minicommerce.payment.domain.PaymentStatus;
import jakarta.persistence.*;
import java.math.BigDecimal;
import java.time.Instant;
import java.util.UUID;

/**
 * 支付模块的基础设施适配层：{@code PaymentAttemptEntity}。
 *
 * <p><strong>作用：</strong>负责 JPA、SQL、Redis、RabbitMQ 或外部系统等技术实现，并把技术细节隔离在业务边界之外。
 *
 * <p><strong>为什么：</strong>数据库表和框架会变化；隔离适配器可以避免这些变化扩散到业务规则和 API 契约。
 *
 * <p><strong>对应文档：</strong> {@code 05_auth_security/03_Web常见攻击.md}、 {@code
 * 07_rabbitmq/04_幂等与Outbox.md}、 {@code 11_system_design/04_韧性_Timeout_Retry_Circuit.md}。
 */
@Entity
@Table(
        name = "payment_attempts",
        uniqueConstraints =
                @UniqueConstraint(
                        name = "ux_payment_user_key",
                        columnNames = {"user_id", "idempotency_key"}))
public class PaymentAttemptEntity {
    @Id private UUID id;

    @Column(name = "order_id", nullable = false)
    private UUID orderId;

    @Column(name = "user_id", nullable = false)
    private Long userId;

    @Column(name = "idempotency_key", nullable = false, length = 128)
    private String idempotencyKey;

    @Column(name = "request_hash", nullable = false, length = 64)
    private String requestHash;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false, length = 20)
    private PaymentStatus status;

    @Column(nullable = false, precision = 19, scale = 2)
    private BigDecimal amount;

    @Column(nullable = false, length = 3)
    private String currency;

    @Column(name = "provider_reference", length = 100)
    private String providerReference;

    @Column(name = "last_error", length = 500)
    private String lastError;

    @Column(name = "processing_started_at")
    private Instant processingStartedAt;

    @Column(name = "created_at", nullable = false)
    private Instant createdAt;

    @Column(name = "updated_at", nullable = false)
    private Instant updatedAt;

    @Version
    @Column(nullable = false)
    private long version;

    protected PaymentAttemptEntity() {}

    public PaymentAttemptEntity(
            UUID id,
            UUID order,
            Long user,
            String key,
            String hash,
            BigDecimal amount,
            String currency,
            Instant now) {
        this.id = id;
        orderId = order;
        userId = user;
        idempotencyKey = key;
        requestHash = hash;
        status = PaymentStatus.INITIATED;
        this.amount = amount;
        this.currency = currency;
        createdAt = now;
        updatedAt = now;
    }

    public UUID getId() {
        return id;
    }

    public UUID getOrderId() {
        return orderId;
    }

    public Long getUserId() {
        return userId;
    }

    public String getRequestHash() {
        return requestHash;
    }

    public PaymentStatus getStatus() {
        return status;
    }

    public BigDecimal getAmount() {
        return amount;
    }

    public String getCurrency() {
        return currency;
    }

    public String getProviderReference() {
        return providerReference;
    }

    public String getLastError() {
        return lastError;
    }

    public void succeeded(String ref, Instant now) {
        status = PaymentStatus.SUCCEEDED;
        providerReference = ref;
        updatedAt = now;
    }

    public void declined(String error, Instant now) {
        status = PaymentStatus.DECLINED;
        lastError = error;
        updatedAt = now;
    }

    public void unknown(String error, Instant now) {
        status = PaymentStatus.UNKNOWN;
        lastError = error;
        updatedAt = now;
    }
}
