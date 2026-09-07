package com.example.minicommerce.catalog.domain;

/**
 * 商品的三个状态：草稿、已上架、已归档。
 *
 * <p><strong>作用：</strong>商品的三个状态：草稿、已上架、已归档。
 *
 * <p><strong>为什么：</strong>只有 PUBLISHED 商品允许公开销售；枚举只限制选项，能否改变状态仍要看 ProductEntity 的方法。
 *
 * <p><strong>对应文档：</strong> {@code 02_backend_spring/03_DTO_Entity_Domain与映射.md}、 {@code
 * 06_redis/02_CacheAside_TTL与失效.md}。
 */
public enum ProductStatus {
    DRAFT,
    PUBLISHED,
    ARCHIVED
}
