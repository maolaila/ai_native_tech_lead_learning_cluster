package com.example.minicommerce.cart.infrastructure;

import com.example.minicommerce.shared.persistence.BaseEntity;
import jakarta.persistence.*;

/**
 * 购物车模块的基础设施适配层：{@code CartEntity}。
 *
 * <p><strong>作用：</strong>负责 JPA、SQL、Redis、RabbitMQ 或外部系统等技术实现，并把技术细节隔离在业务边界之外。
 *
 * <p><strong>为什么：</strong>数据库表和框架会变化；隔离适配器可以避免这些变化扩散到业务规则和 API 契约。
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
