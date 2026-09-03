package com.example.minicommerce.catalog.domain;

/**
 * 商品目录模块的领域模型层：{@code ProductStatus}。
 *
 * <p><strong>作用：</strong>表达业务状态、行为和不变量，并尽量保持对 Spring、HTTP 与数据库实现无感。
 *
 * <p><strong>为什么：</strong>领域方法比任意 Setter 更能阻止非法状态，也使测试直接描述业务语言。
 *
 * <p><strong>对应文档：</strong> {@code 02_backend_spring/03_DTO_Entity_Domain与映射.md}、 {@code
 * 06_redis/02_CacheAside_TTL与失效.md}。
 */
public enum ProductStatus {
    DRAFT,
    PUBLISHED,
    ARCHIVED
}
