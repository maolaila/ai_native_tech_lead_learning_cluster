package com.example.minicommerce.catalog.application;

import static com.example.minicommerce.catalog.api.ProductDtos.*;

import com.example.minicommerce.audit.application.AuditService;
import com.example.minicommerce.catalog.domain.ProductStatus;
import com.example.minicommerce.catalog.infrastructure.*;
import com.example.minicommerce.inventory.application.InventoryService;
import com.example.minicommerce.messaging.application.OutboxService;
import com.example.minicommerce.shared.error.*;
import com.example.minicommerce.shared.security.CurrentUser;
import com.example.minicommerce.shared.transaction.AfterCommitExecutor;
import java.util.*;
import java.util.function.Function;
import java.util.stream.Collectors;
import org.springframework.data.domain.*;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

/**
 * 商品目录模块的应用用例编排层：{@code ProductService}。
 *
 * <p><strong>作用：</strong>编排一个完整业务用例，协调领域规则、仓储、外部端口与事务边界。
 *
 * <p><strong>为什么：</strong>事务应该围绕业务动作，而不是分散在 Controller 或每个 Repository 中。
 *
 * <p><strong>对应文档：</strong> {@code 02_backend_spring/03_DTO_Entity_Domain与映射.md}、 {@code
 * 06_redis/02_CacheAside_TTL与失效.md}。
 */
@Service
public class ProductService {
    private final ProductRepository products;
    private final ProductCacheService cache;
    private final InventoryService inventory;
    private final OutboxService outbox;
    private final AfterCommitExecutor afterCommit;
    private final CurrentUser currentUser;
    private final AuditService audit;

    public ProductService(
            ProductRepository products,
            ProductCacheService cache,
            InventoryService inventory,
            OutboxService outbox,
            AfterCommitExecutor afterCommit,
            CurrentUser currentUser,
            AuditService audit) {
        this.products = products;
        this.cache = cache;
        this.inventory = inventory;
        this.outbox = outbox;
        this.afterCommit = afterCommit;
        this.currentUser = currentUser;
        this.audit = audit;
    }

    @Transactional(readOnly = true)
    public ProductResponse getPublic(Long id) {
        return cache.get(
                        id,
                        () ->
                                products.findByIdAndStatus(id, ProductStatus.PUBLISHED)
                                        .map(ProductService::view))
                .orElseThrow(() -> new BusinessException(ErrorCode.PRODUCT_NOT_FOUND, "商品不存在"));
    }

    @Transactional(readOnly = true)
    public Page<ProductResponse> listPublic(Pageable pageable) {
        return products.findByStatus(ProductStatus.PUBLISHED, pageable).map(ProductService::view);
    }

    /** 下单专用权威读取：明确不经过 Redis，防止旧价格参与成交。 */
    @Transactional(readOnly = true)
    public Map<Long, ProductEntity> authoritativeSellable(Set<Long> ids) {
        return products.findAllByIdInAndStatus(ids, ProductStatus.PUBLISHED).stream()
                .collect(Collectors.toMap(ProductEntity::getId, Function.identity()));
    }

    @PreAuthorize("hasRole('ADMIN')")
    @Transactional
    public ProductResponse create(CreateProductRequest request) {
        if (products.existsBySku(request.sku().trim()))
            throw new BusinessException(ErrorCode.IDEMPOTENCY_CONFLICT, "SKU 已存在");
        ProductEntity saved =
                products.save(
                        new ProductEntity(
                                request.sku().trim(),
                                request.name().trim(),
                                request.description(),
                                request.price(),
                                request.currency()));
        inventory.initialize(saved.getId(), request.initialStock());
        outbox.append(
                "PRODUCT",
                String.valueOf(saved.getId()),
                "product.changed.v1",
                Map.of("productId", saved.getId()));
        audit.record(
                currentUser.require().id(),
                "PRODUCT_CREATE",
                "PRODUCT",
                saved.getId(),
                null,
                view(saved));
        afterCommit.run(() -> cache.evict(saved.getId()));
        return view(saved);
    }

    @PreAuthorize("hasRole('ADMIN')")
    @Transactional
    public ProductResponse update(Long id, UpdateProductRequest request) {
        ProductEntity product =
                products.findById(id)
                        .orElseThrow(
                                () -> new BusinessException(ErrorCode.PRODUCT_NOT_FOUND, "商品不存在"));
        ProductResponse before = view(product);
        product.update(request.name().trim(), request.description(), request.price());
        outbox.append("PRODUCT", String.valueOf(id), "product.changed.v1", Map.of("productId", id));
        audit.record(
                currentUser.require().id(), "PRODUCT_UPDATE", "PRODUCT", id, before, view(product));
        afterCommit.run(() -> cache.evict(id));
        return view(product);
    }

    @PreAuthorize("hasRole('ADMIN')")
    @Transactional
    public ProductResponse publish(Long id) {
        ProductEntity product =
                products.findById(id)
                        .orElseThrow(
                                () -> new BusinessException(ErrorCode.PRODUCT_NOT_FOUND, "商品不存在"));
        product.publish();
        outbox.append("PRODUCT", String.valueOf(id), "product.changed.v1", Map.of("productId", id));
        afterCommit.run(() -> cache.evict(id));
        return view(product);
    }

    public static ProductResponse view(ProductEntity p) {
        return new ProductResponse(
                p.getId(),
                p.getSku(),
                p.getName(),
                p.getDescription(),
                p.getPrice(),
                p.getCurrency(),
                p.getStatus().name(),
                p.getVersion(),
                p.getUpdatedAt());
    }
}
