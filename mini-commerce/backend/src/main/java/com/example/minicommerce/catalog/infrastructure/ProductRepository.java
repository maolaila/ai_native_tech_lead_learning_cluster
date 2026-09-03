package com.example.minicommerce.catalog.infrastructure;

import com.example.minicommerce.catalog.domain.ProductStatus;
import java.util.Collection;
import java.util.List;
import java.util.Optional;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;

/**
 * 商品目录模块的基础设施适配层：{@code ProductRepository}。
 *
 * <p><strong>作用：</strong>负责 JPA、SQL、Redis、RabbitMQ 或外部系统等技术实现，并把技术细节隔离在业务边界之外。
 *
 * <p><strong>为什么：</strong>数据库表和框架会变化；隔离适配器可以避免这些变化扩散到业务规则和 API 契约。
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
