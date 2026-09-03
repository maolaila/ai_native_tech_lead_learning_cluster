package com.example.minicommerce.inventory.infrastructure;

import jakarta.persistence.*;
import java.time.Instant;

@Entity
@Table(name="inventory")
public class InventoryEntity {
    @Id @Column(name="product_id") private Long productId;
    @Column(nullable=false) private int available;
    @Column(nullable=false) private int reserved;
    @Version @Column(nullable=false) private long version;
    @Column(name="updated_at",nullable=false) private Instant updatedAt;
    protected InventoryEntity(){}
    public InventoryEntity(Long productId,int available){this.productId=productId;this.available=available;this.reserved=0;this.updatedAt=Instant.now();}
    public Long getProductId(){return productId;} public int getAvailable(){return available;} public int getReserved(){return reserved;} public long getVersion(){return version;}
    public void replaceAvailable(int value){if(value<0)throw new IllegalArgumentException("库存不能小于0");available=value;updatedAt=Instant.now();}
}
