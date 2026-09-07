package com.example.minicommerce.inventory.api;

import com.example.minicommerce.inventory.application.InventoryService;
import jakarta.validation.Valid;
import jakarta.validation.constraints.PositiveOrZero;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;

/**
 * 库存 HTTP 入口：读取库存，或由管理员设置可售数量。
 *
 * <p><strong>作用：</strong>库存 HTTP 入口：读取库存，或由管理员设置可售数量。
 *
 * <p><strong>为什么：</strong>数量是否合法是输入校验，能不能修改是权限校验；下单预留通过订单业务调用，不允许随便暴露裸扣库存接口。
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
