package com.example.minicommerce.cart.infrastructure;

import java.util.*;
import org.springframework.data.jpa.repository.JpaRepository;

/**
 * 查询、保存或删除某个购物车中的商品明细。
 *
 * <p><strong>作用：</strong>查询、保存或删除某个购物车中的商品明细。
 *
 * <p><strong>为什么：</strong>查询必须带 cartId，不能只拿 productId 找明细，否则可能碰到其他用户的购物车。
 *
 * <p><strong>对应文档：</strong> {@code 00_start/02_长期项目_Mini_Commerce.md}、 {@code
 * 02_backend_spring/02_Controller_Service_Repository分层.md}、 {@code
 * 04_database_postgresql/01_关系模型_SQL与表关系.md}。
 */
public interface CartItemRepository extends JpaRepository<CartItemEntity, Long> {
    List<CartItemEntity> findByCartIdOrderById(Long cartId);

    Optional<CartItemEntity> findByCartIdAndProductId(Long cartId, Long productId);

    void deleteByCartId(Long cartId);
}
