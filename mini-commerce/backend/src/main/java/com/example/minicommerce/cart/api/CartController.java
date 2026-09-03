package com.example.minicommerce.cart.api;

import com.example.minicommerce.cart.application.CartService;
import com.example.minicommerce.shared.security.CurrentUser;
import jakarta.validation.Valid;
import jakarta.validation.constraints.Positive;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.*;

/**
 * 购物车模块的HTTP/API 适配层：{@code CartController}。
 *
 * <p><strong>作用：</strong>负责路由、请求参数、校验、认证主体和 HTTP 响应转换，不承载核心业务规则。
 *
 * <p><strong>为什么：</strong>把 HTTP 细节留在系统边界，应用服务才能脱离 Web 框架测试和复用。
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
