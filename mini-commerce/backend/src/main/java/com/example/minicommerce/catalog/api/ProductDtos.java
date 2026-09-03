package com.example.minicommerce.catalog.api;

import jakarta.validation.constraints.*;
import java.math.BigDecimal;
import java.time.Instant;

public final class ProductDtos {
    private ProductDtos() {}
    public record CreateProductRequest(@NotBlank @Size(max=64) String sku, @NotBlank @Size(max=200) String name,
        @NotNull @Size(max=2000) String description, @NotNull @DecimalMin("0.01") BigDecimal price,
        @NotBlank @Pattern(regexp="[A-Z]{3}") String currency, @PositiveOrZero int initialStock) {}
    public record UpdateProductRequest(@NotBlank @Size(max=200) String name, @NotNull @Size(max=2000) String description,
        @NotNull @DecimalMin("0.01") BigDecimal price) {}
    public record ProductResponse(Long id, String sku, String name, String description, BigDecimal price,
        String currency, String status, long version, Instant updatedAt) {}
}
