package com.example.minicommerce.catalog.api;

import jakarta.validation.constraints.*;
import java.math.BigDecimal;
import java.time.Instant;

/**
 * 商品目录模块的HTTP/API 适配层：{@code ProductDtos}。
 *
 * <p><strong>作用：</strong>负责路由、请求参数、校验、认证主体和 HTTP 响应转换，不承载核心业务规则。
 *
 * <p><strong>为什么：</strong>把 HTTP 细节留在系统边界，应用服务才能脱离 Web 框架测试和复用。
 *
 * <p><strong>对应文档：</strong> {@code 02_backend_spring/03_DTO_Entity_Domain与映射.md}、 {@code
 * 06_redis/02_CacheAside_TTL与失效.md}。
 */
public final class ProductDtos {
    private ProductDtos() {}

    public record CreateProductRequest(
            @NotBlank @Size(max = 64) String sku,
            @NotBlank @Size(max = 200) String name,
            @NotNull @Size(max = 2000) String description,
            @NotNull @DecimalMin("0.01") BigDecimal price,
            @NotBlank @Pattern(regexp = "[A-Z]{3}") String currency,
            @PositiveOrZero int initialStock) {}

    public record UpdateProductRequest(
            @NotBlank @Size(max = 200) String name,
            @NotNull @Size(max = 2000) String description,
            @NotNull @DecimalMin("0.01") BigDecimal price) {}

    public record ProductResponse(
            Long id,
            String sku,
            String name,
            String description,
            BigDecimal price,
            String currency,
            String status,
            long version,
            Instant updatedAt) {}
}
