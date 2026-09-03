package com.example.minicommerce.inventory.infrastructure;

import jakarta.persistence.*;
import java.time.Instant;

/**
 * 库存模块的基础设施适配层：{@code InventoryEntity}。
 *
 * <p><strong>作用：</strong>负责 JPA、SQL、Redis、RabbitMQ 或外部系统等技术实现，并把技术细节隔离在业务边界之外。
 *
 * <p><strong>为什么：</strong>数据库表和框架会变化；隔离适配器可以避免这些变化扩散到业务规则和 API 契约。
 *
 * <p><strong>对应文档：</strong> {@code 04_database_postgresql/04_事务与Spring边界.md}、 {@code
 * 04_database_postgresql/05_并发_锁与库存超卖.md}、 {@code 04_database_postgresql/06_隔离_MVCC与死锁.md}。
 */
@Entity
@Table(name = "inventory")
public class InventoryEntity {
    @Id
    @Column(name = "product_id")
    private Long productId;

    @Column(nullable = false)
    private int available;

    @Column(nullable = false)
    private int reserved;

    @Version
    @Column(nullable = false)
    private long version;

    @Column(name = "updated_at", nullable = false)
    private Instant updatedAt;

    protected InventoryEntity() {}

    public InventoryEntity(Long productId, int available) {
        this.productId = productId;
        this.available = available;
        this.reserved = 0;
        this.updatedAt = Instant.now();
    }

    public Long getProductId() {
        return productId;
    }

    public int getAvailable() {
        return available;
    }

    public int getReserved() {
        return reserved;
    }

    public long getVersion() {
        return version;
    }

    public void replaceAvailable(int value) {
        if (value < 0) throw new IllegalArgumentException("库存不能小于0");
        available = value;
        updatedAt = Instant.now();
    }
}
