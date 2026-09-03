package com.example.minicommerce.shared.persistence;

import jakarta.persistence.Column;
import jakarta.persistence.MappedSuperclass;
import jakarta.persistence.PrePersist;
import jakarta.persistence.PreUpdate;
import java.time.Instant;

/**
 * 所有 JPA 实体可以继承的基础时间字段。
 *
 * <p><strong>作用：</strong>统一保存记录的创建时间和最后修改时间，避免每个 Entity 重复写相同代码。
 *
 * <p><strong>为什么只表示技术审计时间：</strong>{@code createdAt} 表示“这条数据库记录什么时候创建”。
 * 支付成功时间、订单取消时间等业务时刻仍应使用各自明确字段，不能全部混成一个 {@code updatedAt}。
 *
 * <p><strong>对应文档：</strong> {@code 02_backend_spring/03_DTO_Entity_Domain与映射.md}、 {@code
 * 04_database_postgresql/01_关系模型_SQL与表关系.md}、 {@code
 * mini-commerce/docs/SPRING-JAVA-ANNOTATIONS.md}。
 */
// @MappedSuperclass：这个父类本身不单独对应一张表，但字段会被子 Entity 映射到各自表中。
@MappedSuperclass
public abstract class BaseEntity {

    // updatable = false：记录创建后，普通 UPDATE 不应再修改 created_at。
    @Column(name = "created_at", nullable = false, updatable = false)
    protected Instant createdAt;

    @Column(name = "updated_at", nullable = false)
    protected Instant updatedAt;

    /**
     * JPA 第一次 INSERT 之前自动调用。
     *
     * <p>{@code @PrePersist} 可以理解成“保存新记录前的钩子”。这里为创建时间和更新时间赋值。
     */
    @PrePersist
    void beforeInsert() {
        Instant now = Instant.now();
        if (createdAt == null) {
            createdAt = now;
        }
        updatedAt = now;
    }

    /** JPA 执行 UPDATE 之前自动调用，用当前时间刷新 {@code updatedAt}。 */
    @PreUpdate
    void beforeUpdate() {
        updatedAt = Instant.now();
    }

    public Instant getCreatedAt() {
        return createdAt;
    }

    public Instant getUpdatedAt() {
        return updatedAt;
    }
}
