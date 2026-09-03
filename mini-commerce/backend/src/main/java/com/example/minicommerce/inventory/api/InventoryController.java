package com.example.minicommerce.inventory.api;

import com.example.minicommerce.inventory.application.InventoryService;
import jakarta.validation.Valid;
import jakarta.validation.constraints.PositiveOrZero;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;

/**
 * 库存模块的HTTP/API 适配层：{@code InventoryController}。
 *
 * <p><strong>作用：</strong>负责路由、请求参数、校验、认证主体和 HTTP 响应转换，不承载核心业务规则。
 *
 * <p><strong>为什么：</strong>把 HTTP 细节留在系统边界，应用服务才能脱离 Web 框架测试和复用。
 *
 * <p><strong>对应文档：</strong> {@code 04_database_postgresql/04_事务与Spring边界.md}、 {@code
 * 04_database_postgresql/05_并发_锁与库存超卖.md}、 {@code 04_database_postgresql/06_隔离_MVCC与死锁.md}。
 */
@RestController
@RequestMapping("/api/inventory")
public class InventoryController {
    private final InventoryService service;

    public InventoryController(InventoryService service) {
        this.service = service;
    }

    @GetMapping("/{productId}")
    @PreAuthorize("hasAnyRole('ADMIN','SUPPORT')")
    InventoryService.InventoryView get(@PathVariable Long productId) {
        return service.get(productId);
    }

    @PutMapping("/{productId}")
    @PreAuthorize("hasRole('ADMIN')")
    InventoryService.InventoryView replace(
            @PathVariable Long productId, @Valid @RequestBody ReplaceRequest r) {
        return service.replaceAvailable(productId, r.available());
    }

    public record ReplaceRequest(@PositiveOrZero int available) {}
}
