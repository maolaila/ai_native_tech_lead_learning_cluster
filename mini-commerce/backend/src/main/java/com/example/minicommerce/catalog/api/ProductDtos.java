package com.example.minicommerce.catalog.api;

import jakarta.validation.constraints.*;
import java.math.BigDecimal;
import java.time.Instant;

/**
 * 规定创建商品、修改商品和返回商品时包含哪些字段。
 *
 * <p><strong>作用：</strong>规定创建商品、修改商品和返回商品时包含哪些字段。
 *
 * <p><strong>为什么：</strong>价格是 BigDecimal，限制小数位以匹配数据库；initialStock 是初始可售数量，不是已经卖出的数量。
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
            @NotNull @DecimalMin("0.01") @Digits(integer = 17, fraction = 2) BigDecimal price,
            @NotBlank @Pattern(regexp = "[A-Z]{3}") String currency,
            @PositiveOrZero int initialStock) {}

    public record UpdateProductRequest(
            @NotBlank @Size(max = 200) String name,
            @NotNull @Size(max = 2000) String description,
            @NotNull @DecimalMin("0.01") @Digits(integer = 17, fraction = 2) BigDecimal price) {}

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
