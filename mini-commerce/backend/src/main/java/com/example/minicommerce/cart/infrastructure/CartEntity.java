package com.example.minicommerce.cart.infrastructure;

import com.example.minicommerce.shared.persistence.BaseEntity;
import jakarta.persistence.*;

/**
 * 保存购物车属于哪个用户；商品明细在 cart_items 表。
 *
 * <p><strong>作用：</strong>保存购物车属于哪个用户；商品明细在 cart_items 表。
 *
 * <p><strong>为什么：</strong>购物车不是订单，不保存最终成交金额；下单时仍须重新查询商品价格和库存。
 *
 * <p><strong>对应文档：</strong> {@code 00_start/02_长期项目_Mini_Commerce.md}、 {@code
 * 02_backend_spring/02_Controller_Service_Repository分层.md}、 {@code
 * 04_database_postgresql/01_关系模型_SQL与表关系.md}。
 */
@Entity
@Table(
        name = "carts",
        uniqueConstraints = @UniqueConstraint(name = "ux_cart_user", columnNames = "user_id"))
public class CartEntity extends BaseEntity {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "user_id", nullable = false)
    private Long userId;

    protected CartEntity() {}

    public CartEntity(Long userId) {
        this.userId = userId;
    }

    public Long getId() {
        return id;
    }

    public Long getUserId() {
        return userId;
    }
}
