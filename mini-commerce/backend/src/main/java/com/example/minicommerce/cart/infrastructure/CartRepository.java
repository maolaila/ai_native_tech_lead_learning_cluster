package com.example.minicommerce.cart.infrastructure;

import java.util.Optional;
import org.springframework.data.jpa.repository.JpaRepository;

/**
 * 按用户查找他的购物车主记录。
 *
 * <p><strong>作用：</strong>按用户查找他的购物车主记录。
 *
 * <p><strong>为什么：</strong>一人只有一个购物车由数据库唯一约束兜底；CartService 还按用户串行修改，避免首次并发创建时撞唯一约束。
 *
 * <p><strong>对应文档：</strong> {@code 00_start/02_长期项目_Mini_Commerce.md}、 {@code
 * 02_backend_spring/02_Controller_Service_Repository分层.md}、 {@code
 * 04_database_postgresql/01_关系模型_SQL与表关系.md}。
 */
public interface CartRepository extends JpaRepository<CartEntity, Long> {
    Optional<CartEntity> findByUserId(Long userId);
}
