package com.example.minicommerce.catalog.infrastructure;

import com.example.minicommerce.catalog.domain.ProductStatus;
import com.example.minicommerce.shared.persistence.BaseEntity;
import jakarta.persistence.*;
import java.math.BigDecimal;

/**
 * 保存商品的名称、SKU、价格、币种和上下架状态。
 *
 * <p><strong>作用：</strong>保存商品的名称、SKU、价格、币种和上下架状态。
 *
 * <p><strong>为什么：</strong>这是商品的当前信息，历史成交信息另存在 OrderItemEntity。version 帮助发现并发更新；不会自动代替库存扣减规则。
 *
 * <p><strong>对应文档：</strong> {@code 02_backend_spring/03_DTO_Entity_Domain与映射.md}、 {@code
 * 06_redis/02_CacheAside_TTL与失效.md}。
 */
@Entity
@Table(
        name = "products",
        indexes = {
            @Index(name = "ix_products_status_created", columnList = "status,created_at"),
            @Index(name = "ux_products_sku", columnList = "sku", unique = true)
        })
public class ProductEntity extends BaseEntity {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, length = 64)
    private String sku;

    @Column(nullable = false, length = 200)
    private String name;

    @Column(nullable = false, length = 2000)
    private String description;

    @Column(nullable = false, precision = 19, scale = 2)
    private BigDecimal price;

    @Column(nullable = false, length = 3)
    @org.hibernate.annotations.JdbcTypeCode(org.hibernate.type.SqlTypes.CHAR)
    private String currency;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false, length = 20)
    private ProductStatus status;

    @Version
    @Column(nullable = false)
    private long version;

    protected ProductEntity() {}

    public ProductEntity(
            String sku, String name, String description, BigDecimal price, String currency) {
        this.sku = sku;
        this.name = name;
        this.description = description;
        this.price = price;
        this.currency = currency;
        this.status = ProductStatus.DRAFT;
    }

    public Long getId() {
        return id;
    }

    public String getSku() {
        return sku;
    }

    public String getName() {
        return name;
    }

    public String getDescription() {
        return description;
    }

    public BigDecimal getPrice() {
        return price;
    }

    public String getCurrency() {
        return currency;
    }

    public ProductStatus getStatus() {
        return status;
    }

    public long getVersion() {
        return version;
    }

    public void update(String name, String description, BigDecimal price) {
        this.name = name;
        this.description = description;
        this.price = price;
    }

    public void publish() {
        this.status = ProductStatus.PUBLISHED;
    }

    public void archive() {
        this.status = ProductStatus.ARCHIVED;
    }
}
