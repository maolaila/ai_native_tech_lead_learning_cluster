package com.example.minicommerce.cart.application;

import com.example.minicommerce.cart.infrastructure.*;
import com.example.minicommerce.catalog.application.ProductService;
import com.example.minicommerce.shared.error.*;
import java.util.*;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

/**
 * 购物车模块的应用用例编排层：{@code CartService}。
 *
 * <p><strong>作用：</strong>编排一个完整业务用例，协调领域规则、仓储、外部端口与事务边界。
 *
 * <p><strong>为什么：</strong>事务应该围绕业务动作，而不是分散在 Controller 或每个 Repository 中。
 *
 * <p><strong>对应文档：</strong> {@code 00_start/02_长期项目_Mini_Commerce.md}、 {@code
 * 02_backend_spring/02_Controller_Service_Repository分层.md}、 {@code
 * 04_database_postgresql/01_关系模型_SQL与表关系.md}。
 */
@Service
public class CartService {
    private final CartRepository carts;
    private final CartItemRepository items;
    private final ProductService products;

    public CartService(CartRepository c, CartItemRepository i, ProductService p) {
        carts = c;
        items = i;
        products = p;
    }

    @Transactional
    public CartView put(Long userId, Long productId, int quantity) {
        products.getPublic(productId);
        CartEntity c =
                carts.findByUserId(userId).orElseGet(() -> carts.save(new CartEntity(userId)));
        CartItemEntity item =
                items.findByCartIdAndProductId(c.getId(), productId)
                        .orElseGet(() -> new CartItemEntity(c.getId(), productId, quantity));
        item.changeQuantity(quantity);
        items.save(item);
        return view(c);
    }

    @Transactional
    public void remove(Long userId, Long productId) {
        CartEntity c =
                carts.findByUserId(userId)
                        .orElseThrow(
                                () ->
                                        new BusinessException(
                                                ErrorCode.CART_ITEM_NOT_FOUND, "购物车为空"));
        CartItemEntity i =
                items.findByCartIdAndProductId(c.getId(), productId)
                        .orElseThrow(
                                () ->
                                        new BusinessException(
                                                ErrorCode.CART_ITEM_NOT_FOUND, "购物车项不存在"));
        items.delete(i);
    }

    @Transactional(readOnly = true)
    public CartView get(Long userId) {
        return carts.findByUserId(userId).map(this::view).orElse(new CartView(null, List.of()));
    }

    @Transactional
    public void clear(Long userId) {
        carts.findByUserId(userId).ifPresent(c -> items.deleteByCartId(c.getId()));
    }

    private CartView view(CartEntity c) {
        return new CartView(
                c.getId(),
                items.findByCartIdOrderById(c.getId()).stream()
                        .map(i -> new CartLine(i.getProductId(), i.getQuantity()))
                        .toList());
    }

    public record CartView(Long cartId, List<CartLine> items) {}

    public record CartLine(Long productId, int quantity) {}
}
