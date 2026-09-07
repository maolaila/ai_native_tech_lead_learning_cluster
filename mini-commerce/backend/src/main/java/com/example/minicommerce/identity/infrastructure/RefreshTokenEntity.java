package com.example.minicommerce.identity.infrastructure;

import jakarta.persistence.*;
import java.time.Instant;
import java.util.UUID;

/**
 * 保存刷新令牌的哈希、归属用户、到期时间和撤销时间。
 *
 * <p><strong>作用：</strong>保存刷新令牌的哈希、归属用户、到期时间和撤销时间。
 *
 * <p><strong>为什么：</strong>数据库不保存可直接使用的原令牌；isValidAt 同时检查过期和撤销，不能只判断字符串是否存在。
 *
 * <p><strong>对应文档：</strong> {@code 05_auth_security/01_Session_Cookie_Token.md}、 {@code
 * 05_auth_security/02_RBAC与对象级权限.md}、 {@code 05_auth_security/03_Web常见攻击.md}。
 */
@Entity
@Table(
        name = "refresh_tokens",
        indexes = @Index(name = "ix_refresh_token_hash", columnList = "token_hash", unique = true))
public class RefreshTokenEntity {
    @Id private UUID id;

    @Column(name = "user_id", nullable = false)
    private Long userId;

    @Column(name = "token_hash", nullable = false, length = 64)
    private String tokenHash;

    @Column(name = "expires_at", nullable = false)
    private Instant expiresAt;

    @Column(name = "revoked_at")
    private Instant revokedAt;

    @Column(name = "created_at", nullable = false)
    private Instant createdAt;

    protected RefreshTokenEntity() {}

    public RefreshTokenEntity(
            UUID id, Long userId, String tokenHash, Instant expiresAt, Instant createdAt) {
        this.id = id;
        this.userId = userId;
        this.tokenHash = tokenHash;
        this.expiresAt = expiresAt;
        this.createdAt = createdAt;
    }

    public UUID getId() {
        return id;
    }

    public Long getUserId() {
        return userId;
    }

    public String getTokenHash() {
        return tokenHash;
    }

    public boolean isValidAt(Instant now) {
        return revokedAt == null && expiresAt.isAfter(now);
    }

    public void revoke(Instant now) {
        if (revokedAt == null) revokedAt = now;
    }
}
