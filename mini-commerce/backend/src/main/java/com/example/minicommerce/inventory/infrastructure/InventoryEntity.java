package com.example.minicommerce.inventory.infrastructure;

import jakarta.persistence.*;
import java.time.Instant;

/**
 * 保存一种商品的可售数量 available 和已预留数量 reserved。
 *
 * <p><strong>作用：</strong>保存一种商品的可售数量 available 和已预留数量 reserved。
 *
 * <p><strong>为什么：</strong>下单时从可售转到预留，付款时只减少预留。管理员调整 available 不是调整总仓库数量，不能把已预留部分也算进去。
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
