package com.example.minicommerce.catalog.infrastructure;

import com.example.minicommerce.catalog.domain.ProductStatus;
import java.util.Collection;
import java.util.List;
import java.util.Optional;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;

public interface ProductRepository extends JpaRepository<ProductEntity, Long> {
    Optional<ProductEntity> findByIdAndStatus(Long id, ProductStatus status);
    Page<ProductEntity> findByStatus(ProductStatus status, Pageable pageable);
    List<ProductEntity> findAllByIdInAndStatus(Collection<Long> ids, ProductStatus status);
    boolean existsBySku(String sku);
}
