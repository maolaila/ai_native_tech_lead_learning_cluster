package com.example.minicommerce.catalog.infrastructure;

import com.example.minicommerce.catalog.domain.ProductStatus;
import java.util.Collection;
import java.util.List;
import java.util.Optional;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;

/**
 * 按商品 ID、SKU 和上架状态查询 products 表。
 *
 * <p><strong>作用：</strong>按商品 ID、SKU 和上架状态查询 products 表。
 *
 * <p><strong>为什么：</strong>展示查询和下单查询都需要过滤可售状态；下单直接使用本接口的数据库结果，不能把展示缓存当作成交依据。
 *
 * <p><strong>对应文档：</strong> {@code 02_backend_spring/03_DTO_Entity_Domain与映射.md}、 {@code
 * 06_redis/02_CacheAside_TTL与失效.md}。
 */
public interface ProductRepository extends JpaRepository<ProductEntity, Long> {
    Optional<ProductEntity> findByIdAndStatus(Long id, ProductStatus status);

    Page<ProductEntity> findByStatus(ProductStatus status, Pageable pageable);

    List<ProductEntity> findAllByIdInAndStatus(Collection<Long> ids, ProductStatus status);

    boolean existsBySku(String sku);
}
