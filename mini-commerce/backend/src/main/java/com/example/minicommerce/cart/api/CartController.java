package com.example.minicommerce.cart.api;

import com.example.minicommerce.cart.application.CartService;
import com.example.minicommerce.shared.security.CurrentUser;
import jakarta.validation.Valid;
import jakarta.validation.constraints.Positive;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.*;

/**
 * 接收查看购物车、设置商品数量和移除商品的请求。
 *
 * <p><strong>作用：</strong>接收查看购物车、设置商品数量和移除商品的请求。
 *
 * <p><strong>为什么：</strong>用户 ID 从当前身份取得，不能让请求方随便填写。PUT 设置的是最终数量，不是每重试一次再加一。
 *
 * <p><strong>对应文档：</strong> {@code 00_start/02_长期项目_Mini_Commerce.md}、 {@code
 * 02_backend_spring/02_Controller_Service_Repository分层.md}、 {@code
 * 04_database_postgresql/01_关系模型_SQL与表关系.md}。
 */
@RestController
@RequestMapping("/api/cart")
public class CartController {
    private final CartService service;
    private final CurrentUser current;

    public CartController(CartService s, CurrentUser c) {
        service = s;
        current = c;
    }

    @GetMapping
    CartService.CartView get() {
        return service.get(current.require().id());
    }

    @PutMapping("/items/{productId}")
    CartService.CartView put(@PathVariable Long productId, @Valid @RequestBody QuantityRequest r) {
        return service.put(current.require().id(), productId, r.quantity());
    }

    @DeleteMapping("/items/{productId}")
    @ResponseStatus(HttpStatus.NO_CONTENT)
    void remove(@PathVariable Long productId) {
        service.remove(current.require().id(), productId);
    }

    public record QuantityRequest(@Positive int quantity) {}
}
