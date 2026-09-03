package com.example.minicommerce.catalog.infrastructure;

import com.example.minicommerce.catalog.domain.ProductStatus;
import com.example.minicommerce.shared.persistence.BaseEntity;
import jakarta.persistence.*;
import java.math.BigDecimal;

@Entity
@Table(name = "products", indexes = {
    @Index(name = "ix_products_status_created", columnList = "status,created_at"),
    @Index(name = "ux_products_sku", columnList = "sku", unique = true)
})
public class ProductEntity extends BaseEntity {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    @Column(nullable = false, length = 64) private String sku;
    @Column(nullable = false, length = 200) private String name;
    @Column(nullable = false, length = 2000) private String description;
    @Column(nullable = false, precision = 19, scale = 2) private BigDecimal price;
    @Column(nullable = false, length = 3) private String currency;
    @Enumerated(EnumType.STRING) @Column(nullable = false, length = 20) private ProductStatus status;
    @Version @Column(nullable = false) private long version;

    protected ProductEntity() {}
    public ProductEntity(String sku, String name, String description, BigDecimal price, String currency) {
        this.sku=sku; this.name=name; this.description=description; this.price=price; this.currency=currency; this.status=ProductStatus.DRAFT;
    }
    public Long getId(){return id;} public String getSku(){return sku;} public String getName(){return name;}
    public String getDescription(){return description;} public BigDecimal getPrice(){return price;}
    public String getCurrency(){return currency;} public ProductStatus getStatus(){return status;} public long getVersion(){return version;}
    public void update(String name, String description, BigDecimal price) { this.name=name; this.description=description; this.price=price; }
    public void publish(){ this.status=ProductStatus.PUBLISHED; }
    public void archive(){ this.status=ProductStatus.ARCHIVED; }
}
