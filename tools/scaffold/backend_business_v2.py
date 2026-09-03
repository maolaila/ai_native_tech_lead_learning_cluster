from __future__ import annotations

FILES: dict[str, str] = {
"mini-commerce/backend/src/main/java/com/example/minicommerce/catalog/domain/ProductStatus.java": r'''package com.example.minicommerce.catalog.domain;
public enum ProductStatus { DRAFT, PUBLISHED, ARCHIVED }
''',
"mini-commerce/backend/src/main/java/com/example/minicommerce/catalog/infrastructure/ProductEntity.java": r'''package com.example.minicommerce.catalog.infrastructure;

import com.example.minicommerce.catalog.domain.ProductStatus;
import com.example.minicommerce.shared.persistence.BaseEntity;
import jakarta.persistence.*;
import java.math.BigDecimal;

@Entity
@Table(name = "products", indexes = {
    @Index(name = "ix_products_status_created", columnList = "status,created_at"),
    @Index(name = "ux_products_sku", columnList = "sku", unique = true)
})
public class ProductEntity extends BaseEntity {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    @Column(nullable = false, length = 64) private String sku;
    @Column(nullable = false, length = 200) private String name;
    @Column(nullable = false, length = 2000) private String description;
    @Column(nullable = false, precision = 19, scale = 2) private BigDecimal price;
    @Column(nullable = false, length = 3) private String currency;
    @Enumerated(EnumType.STRING) @Column(nullable = false, length = 20) private ProductStatus status;
    @Version @Column(nullable = false) private long version;

    protected ProductEntity() {}
    public ProductEntity(String sku, String name, String description, BigDecimal price, String currency) {
        this.sku=sku; this.name=name; this.description=description; this.price=price; this.currency=currency; this.status=ProductStatus.DRAFT;
    }
    public Long getId(){return id;} public String getSku(){return sku;} public String getName(){return name;}
    public String getDescription(){return description;} public BigDecimal getPrice(){return price;}
    public String getCurrency(){return currency;} public ProductStatus getStatus(){return status;} public long getVersion(){return version;}
    public void update(String name, String description, BigDecimal price) { this.name=name; this.description=description; this.price=price; }
    public void publish(){ this.status=ProductStatus.PUBLISHED; }
    public void archive(){ this.status=ProductStatus.ARCHIVED; }
}
''',
"mini-commerce/backend/src/main/java/com/example/minicommerce/catalog/infrastructure/ProductRepository.java": r'''package com.example.minicommerce.catalog.infrastructure;

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
''',
"mini-commerce/backend/src/main/java/com/example/minicommerce/catalog/api/ProductDtos.java": r'''package com.example.minicommerce.catalog.api;

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
''',
"mini-commerce/backend/src/main/java/com/example/minicommerce/catalog/application/ProductCacheService.java": r'''package com.example.minicommerce.catalog.application;

import com.example.minicommerce.catalog.api.ProductDtos.ProductResponse;
import com.example.minicommerce.shared.config.AppProperties;
import com.example.minicommerce.shared.redis.RedisLockService;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.time.Duration;
import java.util.Optional;
import java.util.concurrent.ThreadLocalRandom;
import java.util.function.Supplier;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.stereotype.Service;

/**
 * Cache Aside：命中直接返回；Miss 查 PostgreSQL；不存在结果使用短 Null Cache；TTL 加抖动。
 * Redis 失败时商品读取可 Fail Open 回源，但下单永远绕过缓存重新读取权威价格。
 * 对应文档：06_redis/02_CacheAside_TTL与失效.md、06_redis/03_穿透_击穿_雪崩与一致性.md。
 */
@Service
public class ProductCacheService {
    private static final Logger log = LoggerFactory.getLogger(ProductCacheService.class);
    private static final String NULL = "__NULL__";
    private final StringRedisTemplate redis;
    private final ObjectMapper json;
    private final AppProperties properties;
    private final RedisLockService locks;

    public ProductCacheService(StringRedisTemplate redis, ObjectMapper json, AppProperties properties, RedisLockService locks) {
        this.redis=redis; this.json=json; this.properties=properties; this.locks=locks;
    }

    public Optional<ProductResponse> get(Long id, Supplier<Optional<ProductResponse>> loader) {
        String key = "product:v1:" + id;
        try {
            Optional<ProductResponse> cached = decode(redis.opsForValue().get(key));
            if (cached != null) return cached;
            var lock = locks.tryLock("lock:load:" + key, Duration.ofSeconds(3));
            if (lock == null) return loader.get(); // 有其他请求回源时不无限等待，避免线程堆积。
            try {
                cached = decode(redis.opsForValue().get(key));
                if (cached != null) return cached;
                Optional<ProductResponse> loaded = loader.get();
                if (loaded.isPresent()) redis.opsForValue().set(key, json.writeValueAsString(loaded.get()), jittered(properties.cache().productTtl()));
                else redis.opsForValue().set(key, NULL, properties.cache().nullTtl());
                return loaded;
            } finally { locks.release(lock); }
        } catch (RuntimeException | JsonProcessingException ex) {
            log.warn("event=product_cache_failed productId={} reason={}", id, ex.getClass().getSimpleName());
            return loader.get();
        }
    }

    public void evict(Long id) {
        try { redis.delete("product:v1:" + id); }
        catch (RuntimeException ex) { log.warn("event=product_cache_evict_failed productId={}", id); }
    }

    /** null 表示真正的 Cache Miss；Optional.empty 表示 Null Cache 命中。 */
    private Optional<ProductResponse> decode(String raw) throws JsonProcessingException {
        if (raw == null) return null;
        if (NULL.equals(raw)) return Optional.empty();
        return Optional.of(json.readValue(raw, ProductResponse.class));
    }

    private Duration jittered(Duration base) {
        long bound = Math.max(1, properties.cache().ttlJitter().toMillis());
        return base.plusMillis(ThreadLocalRandom.current().nextLong(bound));
    }
}
''',
"mini-commerce/backend/src/main/java/com/example/minicommerce/catalog/application/ProductService.java": r'''package com.example.minicommerce.catalog.application;

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

@Service
public class ProductService {
    private final ProductRepository products; private final ProductCacheService cache; private final InventoryService inventory;
    private final OutboxService outbox; private final AfterCommitExecutor afterCommit; private final CurrentUser currentUser; private final AuditService audit;
    public ProductService(ProductRepository products, ProductCacheService cache, InventoryService inventory, OutboxService outbox,
                          AfterCommitExecutor afterCommit, CurrentUser currentUser, AuditService audit) {
        this.products=products; this.cache=cache; this.inventory=inventory; this.outbox=outbox;
        this.afterCommit=afterCommit; this.currentUser=currentUser; this.audit=audit;
    }

    @Transactional(readOnly=true)
    public ProductResponse getPublic(Long id) {
        return cache.get(id, () -> products.findByIdAndStatus(id, ProductStatus.PUBLISHED).map(ProductService::view))
            .orElseThrow(() -> new BusinessException(ErrorCode.PRODUCT_NOT_FOUND, "商品不存在"));
    }

    @Transactional(readOnly=true)
    public Page<ProductResponse> listPublic(Pageable pageable) {
        return products.findByStatus(ProductStatus.PUBLISHED, pageable).map(ProductService::view);
    }

    /** 下单专用权威读取：明确不经过 Redis，防止旧价格参与成交。 */
    @Transactional(readOnly=true)
    public Map<Long, ProductEntity> authoritativeSellable(Set<Long> ids) {
        return products.findAllByIdInAndStatus(ids, ProductStatus.PUBLISHED).stream()
            .collect(Collectors.toMap(ProductEntity::getId, Function.identity()));
    }

    @PreAuthorize("hasRole('ADMIN')")
    @Transactional
    public ProductResponse create(CreateProductRequest request) {
        if (products.existsBySku(request.sku().trim())) throw new BusinessException(ErrorCode.IDEMPOTENCY_CONFLICT, "SKU 已存在");
        ProductEntity saved=products.save(new ProductEntity(request.sku().trim(), request.name().trim(), request.description(), request.price(), request.currency()));
        inventory.initialize(saved.getId(), request.initialStock());
        outbox.append("PRODUCT", String.valueOf(saved.getId()), "product.changed.v1", Map.of("productId", saved.getId()));
        audit.record(currentUser.require().id(), "PRODUCT_CREATE", "PRODUCT", saved.getId(), null, view(saved));
        afterCommit.run(() -> cache.evict(saved.getId()));
        return view(saved);
    }

    @PreAuthorize("hasRole('ADMIN')")
    @Transactional
    public ProductResponse update(Long id, UpdateProductRequest request) {
        ProductEntity product=products.findById(id).orElseThrow(() -> new BusinessException(ErrorCode.PRODUCT_NOT_FOUND,"商品不存在"));
        ProductResponse before=view(product);
        product.update(request.name().trim(), request.description(), request.price());
        outbox.append("PRODUCT", String.valueOf(id), "product.changed.v1", Map.of("productId", id));
        audit.record(currentUser.require().id(), "PRODUCT_UPDATE", "PRODUCT", id, before, view(product));
        afterCommit.run(() -> cache.evict(id));
        return view(product);
    }

    @PreAuthorize("hasRole('ADMIN')") @Transactional
    public ProductResponse publish(Long id) {
        ProductEntity product=products.findById(id).orElseThrow(() -> new BusinessException(ErrorCode.PRODUCT_NOT_FOUND,"商品不存在"));
        product.publish(); outbox.append("PRODUCT", String.valueOf(id), "product.changed.v1", Map.of("productId", id));
        afterCommit.run(() -> cache.evict(id)); return view(product);
    }

    public static ProductResponse view(ProductEntity p) {
        return new ProductResponse(p.getId(),p.getSku(),p.getName(),p.getDescription(),p.getPrice(),p.getCurrency(),p.getStatus().name(),p.getVersion(),p.getUpdatedAt());
    }
}
''',
"mini-commerce/backend/src/main/java/com/example/minicommerce/catalog/api/ProductController.java": r'''package com.example.minicommerce.catalog.api;

import static com.example.minicommerce.catalog.api.ProductDtos.*;
import com.example.minicommerce.catalog.application.ProductService;
import jakarta.validation.Valid;
import org.springframework.data.domain.*;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.*;

/** 对应文档：02_backend_spring/02_Controller_Service_Repository分层.md。Controller 不直接访问 Repository。 */
@RestController
@RequestMapping("/api/products")
public class ProductController {
    private final ProductService service;
    public ProductController(ProductService service){this.service=service;}
    @GetMapping public Page<ProductResponse> list(@PageableDefault(size=20,sort="createdAt",direction=Sort.Direction.DESC) Pageable p){return service.listPublic(p);}
    @GetMapping("/{id}") public ProductResponse get(@PathVariable Long id){return service.getPublic(id);}
    @PostMapping @ResponseStatus(HttpStatus.CREATED) public ProductResponse create(@Valid @RequestBody CreateProductRequest r){return service.create(r);}
    @PutMapping("/{id}") public ProductResponse update(@PathVariable Long id,@Valid @RequestBody UpdateProductRequest r){return service.update(id,r);}
    @PostMapping("/{id}/publication") public ProductResponse publish(@PathVariable Long id){return service.publish(id);}
}
''',
"mini-commerce/backend/src/main/java/com/example/minicommerce/inventory/infrastructure/InventoryEntity.java": r'''package com.example.minicommerce.inventory.infrastructure;

import jakarta.persistence.*;
import java.time.Instant;

@Entity
@Table(name="inventory")
public class InventoryEntity {
    @Id @Column(name="product_id") private Long productId;
    @Column(nullable=false) private int available;
    @Column(nullable=false) private int reserved;
    @Version @Column(nullable=false) private long version;
    @Column(name="updated_at",nullable=false) private Instant updatedAt;
    protected InventoryEntity(){}
    public InventoryEntity(Long productId,int available){this.productId=productId;this.available=available;this.reserved=0;this.updatedAt=Instant.now();}
    public Long getProductId(){return productId;} public int getAvailable(){return available;} public int getReserved(){return reserved;} public long getVersion(){return version;}
    public void replaceAvailable(int value){if(value<0)throw new IllegalArgumentException("库存不能小于0");available=value;updatedAt=Instant.now();}
}
''',
"mini-commerce/backend/src/main/java/com/example/minicommerce/inventory/infrastructure/InventoryRepository.java": r'''package com.example.minicommerce.inventory.infrastructure;

import java.util.Optional;
import org.springframework.data.jpa.repository.*;
import org.springframework.data.repository.query.Param;
import jakarta.persistence.LockModeType;

public interface InventoryRepository extends JpaRepository<InventoryEntity,Long>{
    @Modifying(flushAutomatically=true,clearAutomatically=true)
    @Query(value="update inventory set available=available-:qty,reserved=reserved+:qty,version=version+1,updated_at=now() where product_id=:id and available>=:qty",nativeQuery=true)
    int reserve(@Param("id")Long id,@Param("qty")int qty);

    @Modifying(flushAutomatically=true,clearAutomatically=true)
    @Query(value="update inventory set available=available+:qty,reserved=reserved-:qty,version=version+1,updated_at=now() where product_id=:id and reserved>=:qty",nativeQuery=true)
    int release(@Param("id")Long id,@Param("qty")int qty);

    @Modifying(flushAutomatically=true,clearAutomatically=true)
    @Query(value="update inventory set reserved=reserved-:qty,version=version+1,updated_at=now() where product_id=:id and reserved>=:qty",nativeQuery=true)
    int confirmSale(@Param("id")Long id,@Param("qty")int qty);

    @Lock(LockModeType.PESSIMISTIC_WRITE) @Query("select i from InventoryEntity i where i.productId=:id")
    Optional<InventoryEntity> findForUpdate(@Param("id")Long id);
}
''',
"mini-commerce/backend/src/main/java/com/example/minicommerce/inventory/application/InventoryService.java": r'''package com.example.minicommerce.inventory.application;

import com.example.minicommerce.inventory.infrastructure.*;
import com.example.minicommerce.shared.error.*;
import java.util.*;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

/**
 * 库存预留使用数据库条件 UPDATE。@Transactional 只保证事务原子性，并不能自动防止两个事务同时读到 stock=1。
 * 对应文档：04_database_postgresql/04_事务与Spring边界.md、04_database_postgresql/05_并发_锁与库存超卖.md。
 */
@Service
public class InventoryService {
    private final InventoryRepository repository;
    public InventoryService(InventoryRepository repository){this.repository=repository;}
    public void initialize(Long productId,int stock){repository.save(new InventoryEntity(productId,stock));}

    public void reserve(Map<Long,Integer> quantities){
        quantities.entrySet().stream().sorted(Map.Entry.comparingByKey()).forEach(e->{
            if(repository.reserve(e.getKey(),e.getValue())!=1)
                throw new BusinessException(ErrorCode.INSUFFICIENT_STOCK,"库存不足",Map.of("productId",e.getKey(),"quantity",e.getValue()));
        });
    }
    public void release(Map<Long,Integer> quantities){
        quantities.entrySet().stream().sorted(Map.Entry.comparingByKey()).forEach(e->{
            if(repository.release(e.getKey(),e.getValue())!=1) throw new IllegalStateException("预留库存数据不一致 productId="+e.getKey());
        });
    }
    public void confirmSale(Map<Long,Integer> quantities){
        quantities.entrySet().stream().sorted(Map.Entry.comparingByKey()).forEach(e->{
            if(repository.confirmSale(e.getKey(),e.getValue())!=1) throw new IllegalStateException("确认库存数据不一致 productId="+e.getKey());
        });
    }

    @Transactional public InventoryView replaceAvailable(Long productId,int available){
        InventoryEntity i=repository.findForUpdate(productId).orElseThrow(()->new BusinessException(ErrorCode.INVENTORY_NOT_FOUND,"库存不存在"));
        i.replaceAvailable(available);return view(i);
    }
    @Transactional(readOnly=true) public InventoryView get(Long productId){return repository.findById(productId).map(InventoryService::view)
        .orElseThrow(()->new BusinessException(ErrorCode.INVENTORY_NOT_FOUND,"库存不存在"));}
    private static InventoryView view(InventoryEntity i){return new InventoryView(i.getProductId(),i.getAvailable(),i.getReserved(),i.getVersion());}
    public record InventoryView(Long productId,int available,int reserved,long version){}
}
''',
"mini-commerce/backend/src/main/java/com/example/minicommerce/inventory/api/InventoryController.java": r'''package com.example.minicommerce.inventory.api;

import com.example.minicommerce.inventory.application.InventoryService;
import jakarta.validation.Valid;
import jakarta.validation.constraints.PositiveOrZero;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;

@RestController @RequestMapping("/api/inventory")
public class InventoryController{
 private final InventoryService service; public InventoryController(InventoryService service){this.service=service;}
 @GetMapping("/{productId}") @PreAuthorize("hasAnyRole('ADMIN','SUPPORT')")
 InventoryService.InventoryView get(@PathVariable Long productId){return service.get(productId);}
 @PutMapping("/{productId}") @PreAuthorize("hasRole('ADMIN')")
 InventoryService.InventoryView replace(@PathVariable Long productId,@Valid @RequestBody ReplaceRequest r){return service.replaceAvailable(productId,r.available());}
 public record ReplaceRequest(@PositiveOrZero int available){}
}
''',
"mini-commerce/backend/src/main/java/com/example/minicommerce/cart/infrastructure/CartEntity.java": r'''package com.example.minicommerce.cart.infrastructure;
import com.example.minicommerce.shared.persistence.BaseEntity; import jakarta.persistence.*;
@Entity @Table(name="carts",uniqueConstraints=@UniqueConstraint(name="ux_cart_user",columnNames="user_id"))
public class CartEntity extends BaseEntity{@Id @GeneratedValue(strategy=GenerationType.IDENTITY)private Long id;@Column(name="user_id",nullable=false)private Long userId;protected CartEntity(){}public CartEntity(Long userId){this.userId=userId;}public Long getId(){return id;}public Long getUserId(){return userId;}}
''',
"mini-commerce/backend/src/main/java/com/example/minicommerce/cart/infrastructure/CartItemEntity.java": r'''package com.example.minicommerce.cart.infrastructure;
import com.example.minicommerce.shared.persistence.BaseEntity; import jakarta.persistence.*;
@Entity @Table(name="cart_items",uniqueConstraints=@UniqueConstraint(name="ux_cart_product",columnNames={"cart_id","product_id"}))
public class CartItemEntity extends BaseEntity{@Id @GeneratedValue(strategy=GenerationType.IDENTITY)private Long id;@Column(name="cart_id",nullable=false)private Long cartId;@Column(name="product_id",nullable=false)private Long productId;@Column(nullable=false)private int quantity;protected CartItemEntity(){}public CartItemEntity(Long c,Long p,int q){cartId=c;productId=p;quantity=q;}public Long getId(){return id;}public Long getCartId(){return cartId;}public Long getProductId(){return productId;}public int getQuantity(){return quantity;}public void changeQuantity(int q){if(q<=0)throw new IllegalArgumentException("quantity");quantity=q;}}
''',
"mini-commerce/backend/src/main/java/com/example/minicommerce/cart/infrastructure/CartRepository.java": r'''package com.example.minicommerce.cart.infrastructure;
import java.util.Optional; import org.springframework.data.jpa.repository.JpaRepository;
public interface CartRepository extends JpaRepository<CartEntity,Long>{Optional<CartEntity> findByUserId(Long userId);}
''',
"mini-commerce/backend/src/main/java/com/example/minicommerce/cart/infrastructure/CartItemRepository.java": r'''package com.example.minicommerce.cart.infrastructure;
import java.util.*; import org.springframework.data.jpa.repository.JpaRepository;
public interface CartItemRepository extends JpaRepository<CartItemEntity,Long>{List<CartItemEntity> findByCartIdOrderById(Long cartId);Optional<CartItemEntity> findByCartIdAndProductId(Long cartId,Long productId);void deleteByCartId(Long cartId);}
''',
"mini-commerce/backend/src/main/java/com/example/minicommerce/cart/application/CartService.java": r'''package com.example.minicommerce.cart.application;

import com.example.minicommerce.cart.infrastructure.*;import com.example.minicommerce.catalog.application.ProductService;import com.example.minicommerce.shared.error.*;import java.util.*;import org.springframework.stereotype.Service;import org.springframework.transaction.annotation.Transactional;

@Service public class CartService{
 private final CartRepository carts;private final CartItemRepository items;private final ProductService products;
 public CartService(CartRepository c,CartItemRepository i,ProductService p){carts=c;items=i;products=p;}
 @Transactional public CartView put(Long userId,Long productId,int quantity){products.getPublic(productId);CartEntity c=carts.findByUserId(userId).orElseGet(()->carts.save(new CartEntity(userId)));CartItemEntity item=items.findByCartIdAndProductId(c.getId(),productId).orElseGet(()->new CartItemEntity(c.getId(),productId,quantity));item.changeQuantity(quantity);items.save(item);return view(c);}
 @Transactional public void remove(Long userId,Long productId){CartEntity c=carts.findByUserId(userId).orElseThrow(()->new BusinessException(ErrorCode.CART_ITEM_NOT_FOUND,"购物车为空"));CartItemEntity i=items.findByCartIdAndProductId(c.getId(),productId).orElseThrow(()->new BusinessException(ErrorCode.CART_ITEM_NOT_FOUND,"购物车项不存在"));items.delete(i);}
 @Transactional(readOnly=true) public CartView get(Long userId){return carts.findByUserId(userId).map(this::view).orElse(new CartView(null,List.of()));}
 @Transactional public void clear(Long userId){carts.findByUserId(userId).ifPresent(c->items.deleteByCartId(c.getId()));}
 private CartView view(CartEntity c){return new CartView(c.getId(),items.findByCartIdOrderById(c.getId()).stream().map(i->new CartLine(i.getProductId(),i.getQuantity())).toList());}
 public record CartView(Long cartId,List<CartLine> items){}public record CartLine(Long productId,int quantity){}
}
''',
"mini-commerce/backend/src/main/java/com/example/minicommerce/cart/api/CartController.java": r'''package com.example.minicommerce.cart.api;
import com.example.minicommerce.cart.application.CartService;import com.example.minicommerce.shared.security.CurrentUser;import jakarta.validation.Valid;import jakarta.validation.constraints.Positive;import org.springframework.http.HttpStatus;import org.springframework.web.bind.annotation.*;
@RestController @RequestMapping("/api/cart") public class CartController{private final CartService service;private final CurrentUser current;public CartController(CartService s,CurrentUser c){service=s;current=c;}@GetMapping CartService.CartView get(){return service.get(current.require().id());}@PutMapping("/items/{productId}") CartService.CartView put(@PathVariable Long productId,@Valid @RequestBody QuantityRequest r){return service.put(current.require().id(),productId,r.quantity());}@DeleteMapping("/items/{productId}")@ResponseStatus(HttpStatus.NO_CONTENT)void remove(@PathVariable Long productId){service.remove(current.require().id(),productId);}public record QuantityRequest(@Positive int quantity){}}
''',
"mini-commerce/backend/src/main/java/com/example/minicommerce/promotion/domain/CouponType.java": r'''package com.example.minicommerce.promotion.domain;public enum CouponType{PERCENT,FIXED}
''',
"mini-commerce/backend/src/main/java/com/example/minicommerce/promotion/domain/UserCouponStatus.java": r'''package com.example.minicommerce.promotion.domain;public enum UserCouponStatus{ISSUED,RESERVED,USED,EXPIRED}
''',
"mini-commerce/backend/src/main/java/com/example/minicommerce/promotion/infrastructure/CouponEntity.java": r'''package com.example.minicommerce.promotion.infrastructure;
import com.example.minicommerce.promotion.domain.CouponType;import jakarta.persistence.*;import java.math.BigDecimal;import java.time.Instant;
@Entity @Table(name="coupons",indexes=@Index(name="ux_coupon_code",columnList="code",unique=true)) public class CouponEntity{@Id@GeneratedValue(strategy=GenerationType.IDENTITY)private Long id;@Column(nullable=false,length=50)private String code;@Enumerated(EnumType.STRING)@Column(nullable=false,length=20)private CouponType type;@Column(nullable=false,precision=19,scale=2)private BigDecimal value;@Column(name="min_amount",nullable=false,precision=19,scale=2)private BigDecimal minAmount;@Column(name="max_discount",precision=19,scale=2)private BigDecimal maxDiscount;@Column(name="valid_from",nullable=false)private Instant validFrom;@Column(name="valid_until",nullable=false)private Instant validUntil;@Column(nullable=false)private boolean active;protected CouponEntity(){}public CouponEntity(String c,CouponType t,BigDecimal v,BigDecimal m,BigDecimal max,Instant from,Instant until){code=c;type=t;value=v;minAmount=m;maxDiscount=max;validFrom=from;validUntil=until;active=true;}public Long getId(){return id;}public String getCode(){return code;}public CouponType getType(){return type;}public BigDecimal getValue(){return value;}public BigDecimal getMinAmount(){return minAmount;}public BigDecimal getMaxDiscount(){return maxDiscount;}public boolean validAt(Instant n){return active&&!n.isBefore(validFrom)&&n.isBefore(validUntil);}}
''',
"mini-commerce/backend/src/main/java/com/example/minicommerce/promotion/infrastructure/UserCouponEntity.java": r'''package com.example.minicommerce.promotion.infrastructure;
import com.example.minicommerce.promotion.domain.UserCouponStatus;import jakarta.persistence.*;import java.util.UUID;
@Entity @Table(name="user_coupons",uniqueConstraints=@UniqueConstraint(name="ux_user_coupon",columnNames={"user_id","coupon_id"})) public class UserCouponEntity{@Id@GeneratedValue(strategy=GenerationType.IDENTITY)private Long id;@Column(name="user_id",nullable=false)private Long userId;@Column(name="coupon_id",nullable=false)private Long couponId;@Enumerated(EnumType.STRING)@Column(nullable=false,length=20)private UserCouponStatus status;@Column(name="reserved_order_id")private UUID reservedOrderId;@Version@Column(nullable=false)private long version;protected UserCouponEntity(){}public UserCouponEntity(Long u,Long c){userId=u;couponId=c;status=UserCouponStatus.ISSUED;}public Long getId(){return id;}public Long getUserId(){return userId;}public Long getCouponId(){return couponId;}public UserCouponStatus getStatus(){return status;}public void reserve(UUID orderId){if(status!=UserCouponStatus.ISSUED)throw new IllegalStateException("coupon not issued");status=UserCouponStatus.RESERVED;reservedOrderId=orderId;}public void markUsed(UUID orderId){if(status==UserCouponStatus.USED)return;if(status!=UserCouponStatus.RESERVED||!orderId.equals(reservedOrderId))throw new IllegalStateException("coupon reservation mismatch");status=UserCouponStatus.USED;}public void release(UUID orderId){if(status==UserCouponStatus.RESERVED&&orderId.equals(reservedOrderId)){status=UserCouponStatus.ISSUED;reservedOrderId=null;}}}
''',
"mini-commerce/backend/src/main/java/com/example/minicommerce/promotion/infrastructure/CouponRepository.java": r'''package com.example.minicommerce.promotion.infrastructure;import java.util.Optional;import org.springframework.data.jpa.repository.JpaRepository;public interface CouponRepository extends JpaRepository<CouponEntity,Long>{Optional<CouponEntity> findByCodeIgnoreCase(String code);}
''',
"mini-commerce/backend/src/main/java/com/example/minicommerce/promotion/infrastructure/UserCouponRepository.java": r'''package com.example.minicommerce.promotion.infrastructure;
import java.util.Optional;import org.springframework.data.jpa.repository.*;import org.springframework.data.repository.query.Param;import jakarta.persistence.LockModeType;
public interface UserCouponRepository extends JpaRepository<UserCouponEntity,Long>{@Lock(LockModeType.PESSIMISTIC_WRITE)@Query("select u from UserCouponEntity u where u.userId=:userId and u.couponId=:couponId")Optional<UserCouponEntity> findForUpdate(@Param("userId")Long userId,@Param("couponId")Long couponId);}
''',
"mini-commerce/backend/src/main/java/com/example/minicommerce/promotion/application/CouponService.java": r'''package com.example.minicommerce.promotion.application;

import com.example.minicommerce.promotion.domain.*;import com.example.minicommerce.promotion.infrastructure.*;import com.example.minicommerce.shared.error.*;import java.math.*;import java.time.Clock;import java.util.*;import org.springframework.stereotype.Service;

/** 对应文档：03_testing/02_测试用例设计.md。最低金额、有效期、归属和一次性使用都在服务端验证。 */
@Service public class CouponService{
 private final CouponRepository coupons;private final UserCouponRepository userCoupons;private final Clock clock;
 public CouponService(CouponRepository c,UserCouponRepository u,Clock clock){coupons=c;userCoupons=u;this.clock=clock;}
 public CouponReservation reserve(String code,Long userId,BigDecimal subtotal,UUID orderId){if(code==null||code.isBlank())return CouponReservation.none();CouponEntity c=coupons.findByCodeIgnoreCase(code.trim()).orElseThrow(()->new BusinessException(ErrorCode.COUPON_NOT_FOUND,"优惠券不存在"));if(!c.validAt(clock.instant())||subtotal.compareTo(c.getMinAmount())<0)throw new BusinessException(ErrorCode.COUPON_NOT_APPLICABLE,"优惠券不可用");UserCouponEntity uc=userCoupons.findForUpdate(userId,c.getId()).orElseThrow(()->new BusinessException(ErrorCode.COUPON_NOT_APPLICABLE,"优惠券不属于当前用户"));if(uc.getStatus()!=UserCouponStatus.ISSUED)throw new BusinessException(ErrorCode.COUPON_ALREADY_USED,"优惠券已使用或被占用");BigDecimal discount=c.getType()==CouponType.PERCENT?subtotal.multiply(c.getValue()).divide(BigDecimal.valueOf(100),2,RoundingMode.HALF_UP):c.getValue();if(c.getMaxDiscount()!=null&&discount.compareTo(c.getMaxDiscount())>0)discount=c.getMaxDiscount();if(discount.compareTo(subtotal)>0)discount=subtotal;uc.reserve(orderId);return new CouponReservation(uc.getId(),discount.setScale(2,RoundingMode.HALF_UP));}
 public void markUsed(Long id,UUID orderId){if(id!=null)userCoupons.findById(id).orElseThrow().markUsed(orderId);}public void release(Long id,UUID orderId){if(id!=null)userCoupons.findById(id).ifPresent(c->c.release(orderId));}
 public record CouponReservation(Long userCouponId,BigDecimal discount){public static CouponReservation none(){return new CouponReservation(null,BigDecimal.ZERO.setScale(2));}}
}
''',
"mini-commerce/backend/src/main/java/com/example/minicommerce/order/domain/OrderStatus.java": r'''package com.example.minicommerce.order.domain;public enum OrderStatus{PENDING_PAYMENT,PAID,FULFILLING,COMPLETED,CANCELLED,REFUNDING,REFUNDED}
''',
"mini-commerce/backend/src/main/java/com/example/minicommerce/order/infrastructure/OrderEntity.java": r'''package com.example.minicommerce.order.infrastructure;

import com.example.minicommerce.order.domain.OrderStatus;import jakarta.persistence.*;import java.math.BigDecimal;import java.time.Instant;import java.util.UUID;
/** 订单状态只能通过领域方法转换，禁止任意 setStatus。对应文档：00_start/02_长期项目_Mini_Commerce.md。 */
@Entity @Table(name="orders",indexes={@Index(name="ix_orders_user_created",columnList="user_id,created_at"),@Index(name="ix_orders_status_created",columnList="status,created_at")})
public class OrderEntity{@Id private UUID id;@Column(name="order_number",nullable=false,unique=true,length=40)private String orderNumber;@Column(name="user_id",nullable=false)private Long userId;@Enumerated(EnumType.STRING)@Column(nullable=false,length=30)private OrderStatus status;@Column(nullable=false,precision=19,scale=2)private BigDecimal subtotal;@Column(nullable=false,precision=19,scale=2)private BigDecimal discount;@Column(name="total_amount",nullable=false,precision=19,scale=2)private BigDecimal totalAmount;@Column(nullable=false,length=3)private String currency;@Column(name="user_coupon_id")private Long userCouponId;@Column(name="payment_id")private UUID paymentId;@Column(name="created_at",nullable=false)private Instant createdAt;@Column(name="updated_at",nullable=false)private Instant updatedAt;@Column(name="cancelled_at")private Instant cancelledAt;@Version@Column(nullable=false)private long version;protected OrderEntity(){}public OrderEntity(UUID id,String number,Long userId,BigDecimal subtotal,BigDecimal discount,BigDecimal total,String currency,Long userCouponId,Instant now){this.id=id;orderNumber=number;this.userId=userId;status=OrderStatus.PENDING_PAYMENT;this.subtotal=subtotal;this.discount=discount;totalAmount=total;this.currency=currency;this.userCouponId=userCouponId;createdAt=now;updatedAt=now;}public UUID getId(){return id;}public String getOrderNumber(){return orderNumber;}public Long getUserId(){return userId;}public OrderStatus getStatus(){return status;}public BigDecimal getSubtotal(){return subtotal;}public BigDecimal getDiscount(){return discount;}public BigDecimal getTotalAmount(){return totalAmount;}public String getCurrency(){return currency;}public Long getUserCouponId(){return userCouponId;}public UUID getPaymentId(){return paymentId;}public Instant getCreatedAt(){return createdAt;}public long getVersion(){return version;}
 public void cancel(Instant now){if(status==OrderStatus.CANCELLED)return;if(status!=OrderStatus.PENDING_PAYMENT)throw new BusinessException(ErrorCode.ORDER_NOT_CANCELLABLE,"当前订单状态不允许取消",Map.of("status",status));status=OrderStatus.CANCELLED;cancelledAt=now;updatedAt=now;}
 public void markPaid(UUID paymentId,Instant now){if(status==OrderStatus.PAID&&Objects.equals(this.paymentId,paymentId))return;if(status!=OrderStatus.PENDING_PAYMENT)throw new BusinessException(ErrorCode.ORDER_NOT_PAYABLE,"当前订单状态不允许支付",Map.of("status",status));this.paymentId=paymentId;status=OrderStatus.PAID;updatedAt=now;}
 public void requestRefund(Instant now){if(status!=OrderStatus.PAID&&status!=OrderStatus.FULFILLING)throw new BusinessException(ErrorCode.ORDER_NOT_REFUNDABLE,"当前订单状态不允许退款");status=OrderStatus.REFUNDING;updatedAt=now;}
 public void markRefunded(Instant now){if(status!=OrderStatus.REFUNDING)throw new BusinessException(ErrorCode.ORDER_NOT_REFUNDABLE,"订单未处于退款中");status=OrderStatus.REFUNDED;updatedAt=now;}
}
'''.replace('import java.util.UUID;','import java.util.UUID;import java.util.Map;import java.util.Objects;import com.example.minicommerce.shared.error.*;'),
"mini-commerce/backend/src/main/java/com/example/minicommerce/order/infrastructure/OrderItemEntity.java": r'''package com.example.minicommerce.order.infrastructure;
import jakarta.persistence.*;import java.math.BigDecimal;import java.util.UUID;
/** 保存成交时名称、SKU 和价格快照；商品后续改名改价不能篡改历史事实。 */
@Entity @Table(name="order_items",uniqueConstraints=@UniqueConstraint(name="ux_order_product",columnNames={"order_id","product_id"}))public class OrderItemEntity{@Id private UUID id;@Column(name="order_id",nullable=false)private UUID orderId;@Column(name="product_id",nullable=false)private Long productId;@Column(name="product_name_snapshot",nullable=false,length=200)private String productName;@Column(name="sku_snapshot",nullable=false,length=64)private String sku;@Column(name="unit_price_snapshot",nullable=false,precision=19,scale=2)private BigDecimal unitPrice;@Column(nullable=false)private int quantity;@Column(name="line_total",nullable=false,precision=19,scale=2)private BigDecimal lineTotal;protected OrderItemEntity(){}public OrderItemEntity(UUID orderId,Long productId,String name,String sku,BigDecimal price,int quantity){id=UUID.randomUUID();this.orderId=orderId;this.productId=productId;productName=name;this.sku=sku;unitPrice=price;this.quantity=quantity;lineTotal=price.multiply(BigDecimal.valueOf(quantity));}public UUID getId(){return id;}public UUID getOrderId(){return orderId;}public Long getProductId(){return productId;}public String getProductName(){return productName;}public String getSku(){return sku;}public BigDecimal getUnitPrice(){return unitPrice;}public int getQuantity(){return quantity;}public BigDecimal getLineTotal(){return lineTotal;}}
''',
"mini-commerce/backend/src/main/java/com/example/minicommerce/order/infrastructure/OrderRepository.java": r'''package com.example.minicommerce.order.infrastructure;
import java.util.*;import org.springframework.data.domain.*;import org.springframework.data.jpa.repository.*;import org.springframework.data.repository.query.Param;import jakarta.persistence.LockModeType;
public interface OrderRepository extends JpaRepository<OrderEntity,UUID>{@Lock(LockModeType.PESSIMISTIC_WRITE)@Query("select o from OrderEntity o where o.id=:id")Optional<OrderEntity> findForUpdate(@Param("id")UUID id);Page<OrderEntity> findByUserId(Long userId,Pageable pageable);}
''',
"mini-commerce/backend/src/main/java/com/example/minicommerce/order/infrastructure/OrderItemRepository.java": r'''package com.example.minicommerce.order.infrastructure;import java.util.*;import org.springframework.data.jpa.repository.JpaRepository;public interface OrderItemRepository extends JpaRepository<OrderItemEntity,UUID>{List<OrderItemEntity> findByOrderIdOrderById(UUID orderId);}
''',
"mini-commerce/backend/src/main/java/com/example/minicommerce/order/infrastructure/IdempotencyRecordEntity.java": r'''package com.example.minicommerce.order.infrastructure;
import jakarta.persistence.*;import java.time.Instant;import java.util.UUID;
@Entity @Table(name="idempotency_records",uniqueConstraints=@UniqueConstraint(name="ux_idempotency_user_key",columnNames={"user_id","idempotency_key"}))public class IdempotencyRecordEntity{@Id private UUID id;@Column(name="user_id",nullable=false)private Long userId;@Column(name="idempotency_key",nullable=false,length=128)private String key;@Column(name="request_hash",nullable=false,length=64)private String requestHash;@Column(nullable=false,length=20)private String status;@Column(name="resource_id")private UUID resourceId;@Column(name="created_at",nullable=false)private Instant createdAt;@Column(name="expires_at",nullable=false)private Instant expiresAt;protected IdempotencyRecordEntity(){}public IdempotencyRecordEntity(Long u,String k,String h,Instant now){id=UUID.randomUUID();userId=u;key=k;requestHash=h;status="PROCESSING";createdAt=now;expiresAt=now.plusSeconds(86400);}public String getRequestHash(){return requestHash;}public String getStatus(){return status;}public UUID getResourceId(){return resourceId;}public void complete(UUID id){resourceId=id;status="COMPLETED";}}
''',
"mini-commerce/backend/src/main/java/com/example/minicommerce/order/infrastructure/IdempotencyRecordRepository.java": r'''package com.example.minicommerce.order.infrastructure;import java.util.*;import org.springframework.data.jpa.repository.JpaRepository;public interface IdempotencyRecordRepository extends JpaRepository<IdempotencyRecordEntity,UUID>{Optional<IdempotencyRecordEntity> findByUserIdAndKey(Long userId,String key);}
''',
"mini-commerce/backend/src/main/java/com/example/minicommerce/order/application/IdempotencyLock.java": r'''package com.example.minicommerce.order.application;
import java.sql.PreparedStatement;import org.springframework.jdbc.core.*;import org.springframework.stereotype.Component;
/**
 * PostgreSQL 事务级 advisory lock 只串行化“同一用户+同一幂等键”。第二个并发请求等待后会看到第一个已提交结果。
 * 对应文档：03_testing/06_API与契约测试.md、07_rabbitmq/04_幂等与Outbox.md。
 */
@Component public class IdempotencyLock{private final JdbcTemplate jdbc;public IdempotencyLock(JdbcTemplate jdbc){this.jdbc=jdbc;}public void acquire(String key){jdbc.execute((ConnectionCallback<Void>)c->{try(PreparedStatement ps=c.prepareStatement("select pg_advisory_xact_lock(hashtextextended(?,0))")){ps.setString(1,key);ps.execute();return null;}});}}
''',
"mini-commerce/backend/src/main/java/com/example/minicommerce/order/application/RequestFingerprint.java": r'''package com.example.minicommerce.order.application;
import com.fasterxml.jackson.databind.ObjectMapper;import java.nio.charset.StandardCharsets;import java.security.*;import java.util.*;import java.util.HexFormat;import org.springframework.stereotype.Component;
@Component public class RequestFingerprint{private final ObjectMapper json;public RequestFingerprint(ObjectMapper json){this.json=json;}public String order(SortedMap<Long,Integer> items,String coupon){try{byte[] data=json.writeValueAsBytes(Map.of("items",items,"coupon",coupon==null?"":coupon.trim().toUpperCase()));return HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(data));}catch(Exception e){throw new IllegalStateException(e);}}}
''',
"mini-commerce/backend/src/main/java/com/example/minicommerce/order/api/OrderDtos.java": r'''package com.example.minicommerce.order.api;
import jakarta.validation.Valid;import jakarta.validation.constraints.*;import java.math.BigDecimal;import java.time.Instant;import java.util.*;
public final class OrderDtos{private OrderDtos(){}public record CreateOrderRequest(@NotEmpty @Size(max=50)List<@Valid OrderLineRequest> items,@Size(max=50)String couponCode){}public record OrderLineRequest(@NotNull Long productId,@Positive int quantity){}public record OrderResponse(UUID id,String orderNumber,Long userId,String status,BigDecimal subtotal,BigDecimal discount,BigDecimal totalAmount,String currency,List<OrderLineResponse>items,Instant createdAt){}public record OrderLineResponse(Long productId,String productName,String sku,BigDecimal unitPrice,int quantity,BigDecimal lineTotal){}}
''',
"mini-commerce/backend/src/main/java/com/example/minicommerce/order/application/OrderMapper.java": r'''package com.example.minicommerce.order.application;
import static com.example.minicommerce.order.api.OrderDtos.*;import com.example.minicommerce.order.infrastructure.*;import java.util.*;
public final class OrderMapper{private OrderMapper(){}public static OrderResponse view(OrderEntity o,List<OrderItemEntity>items){return new OrderResponse(o.getId(),o.getOrderNumber(),o.getUserId(),o.getStatus().name(),o.getSubtotal(),o.getDiscount(),o.getTotalAmount(),o.getCurrency(),items.stream().map(i->new OrderLineResponse(i.getProductId(),i.getProductName(),i.getSku(),i.getUnitPrice(),i.getQuantity(),i.getLineTotal())).toList(),o.getCreatedAt());}}
''',
"mini-commerce/backend/src/main/java/com/example/minicommerce/order/application/OrderQueryService.java": r'''package com.example.minicommerce.order.application;
import static com.example.minicommerce.order.api.OrderDtos.*;import com.example.minicommerce.order.infrastructure.*;import com.example.minicommerce.shared.error.*;import com.example.minicommerce.shared.security.UserPrincipal;import java.util.*;import org.springframework.data.domain.*;import org.springframework.stereotype.Service;import org.springframework.transaction.annotation.Transactional;
@Service public class OrderQueryService{private final OrderRepository orders;private final OrderItemRepository items;public OrderQueryService(OrderRepository o,OrderItemRepository i){orders=o;items=i;}@Transactional(readOnly=true)public OrderResponse get(UUID id,UserPrincipal actor){OrderEntity o=orders.findById(id).orElseThrow(()->new BusinessException(ErrorCode.ORDER_NOT_FOUND,"订单不存在"));authorize(o,actor);return view(o);}@Transactional(readOnly=true)public Page<OrderResponse> list(UserPrincipal actor,Pageable p){Page<OrderEntity> page=actor.role().name().equals("ADMIN")?orders.findAll(p):orders.findByUserId(actor.id(),p);return page.map(this::view);}public OrderResponse view(OrderEntity o){return OrderMapper.view(o,items.findByOrderIdOrderById(o.getId()));}public void authorize(OrderEntity o,UserPrincipal a){if(!o.getUserId().equals(a.id())&&!a.role().name().equals("ADMIN")&&!a.role().name().equals("SUPPORT"))throw new BusinessException(ErrorCode.ACCESS_DENIED,"不能访问他人的订单");}}
''',
"mini-commerce/backend/src/main/java/com/example/minicommerce/order/application/CreateOrderService.java": r'''package com.example.minicommerce.order.application;

import static com.example.minicommerce.order.api.OrderDtos.*;import com.example.minicommerce.audit.application.AuditService;import com.example.minicommerce.catalog.application.ProductService;import com.example.minicommerce.catalog.infrastructure.ProductEntity;import com.example.minicommerce.inventory.application.InventoryService;import com.example.minicommerce.messaging.application.OutboxService;import com.example.minicommerce.order.infrastructure.*;import com.example.minicommerce.promotion.application.CouponService;import com.example.minicommerce.shared.error.*;import io.micrometer.core.instrument.MeterRegistry;import java.math.*;import java.time.Clock;import java.time.format.DateTimeFormatter;import java.util.*;import org.slf4j.MDC;import org.springframework.stereotype.Service;import org.springframework.transaction.annotation.Transactional;

/**
 * 创建订单的强一致事务边界：权威商品读取、服务端计价、库存预留、优惠券占用、订单快照、幂等和 Outbox 同时提交或同时回滚。
 * 对应文档：02_backend_spring/06_订单模块案例.md、04_database_postgresql/04_事务与Spring边界.md、07_rabbitmq/04_幂等与Outbox.md。
 */
@Service public class CreateOrderService{
 private final ProductService products;private final InventoryService inventory;private final CouponService coupons;private final OrderRepository orders;private final OrderItemRepository items;private final IdempotencyRecordRepository idempotency;private final IdempotencyLock lock;private final RequestFingerprint fingerprints;private final OutboxService outbox;private final OrderQueryService query;private final AuditService audit;private final Clock clock;private final MeterRegistry metrics;
 public CreateOrderService(ProductService p,InventoryService i,CouponService c,OrderRepository o,OrderItemRepository oi,IdempotencyRecordRepository ir,IdempotencyLock l,RequestFingerprint f,OutboxService out,OrderQueryService q,AuditService a,Clock clock,MeterRegistry m){products=p;inventory=i;coupons=c;orders=o;items=oi;idempotency=ir;lock=l;fingerprints=f;outbox=out;query=q;audit=a;this.clock=clock;metrics=m;}
 @Transactional public OrderResponse create(Long userId,String key,CreateOrderRequest request){if(key==null||key.isBlank())throw new BusinessException(ErrorCode.IDEMPOTENCY_KEY_REQUIRED,"创建订单必须提供 Idempotency-Key");if(key.length()>128)throw new BusinessException(ErrorCode.VALIDATION_ERROR,"Idempotency-Key 过长");SortedMap<Long,Integer> quantities=normalize(request);String hash=fingerprints.order(quantities,request.couponCode());lock.acquire(userId+":"+key);Optional<IdempotencyRecordEntity> prior=idempotency.findByUserIdAndKey(userId,key);if(prior.isPresent()){IdempotencyRecordEntity r=prior.get();if(!r.getRequestHash().equals(hash))throw new BusinessException(ErrorCode.IDEMPOTENCY_CONFLICT,"同一幂等键不能用于不同请求");if("COMPLETED".equals(r.getStatus()))return query.view(orders.findById(r.getResourceId()).orElseThrow());}
 var now=clock.instant();IdempotencyRecordEntity record=idempotency.save(new IdempotencyRecordEntity(userId,key,hash,now));Map<Long,ProductEntity> found=products.authoritativeSellable(quantities.keySet());if(found.size()!=quantities.size()){Set<Long>missing=new TreeSet<>(quantities.keySet());missing.removeAll(found.keySet());throw new BusinessException(ErrorCode.PRODUCT_NOT_SELLABLE,"商品不存在或不可售",Map.of("productIds",missing));}String currency=found.values().iterator().next().getCurrency();if(found.values().stream().anyMatch(p->!currency.equals(p.getCurrency())))throw new BusinessException(ErrorCode.VALIDATION_ERROR,"一个订单不能混用多币种");BigDecimal subtotal=quantities.entrySet().stream().map(e->found.get(e.getKey()).getPrice().multiply(BigDecimal.valueOf(e.getValue()))).reduce(BigDecimal.ZERO,BigDecimal::add).setScale(2,RoundingMode.HALF_UP);UUID orderId=UUID.randomUUID();var coupon=coupons.reserve(request.couponCode(),userId,subtotal,orderId);inventory.reserve(quantities);BigDecimal total=subtotal.subtract(coupon.discount()).max(BigDecimal.ZERO).setScale(2,RoundingMode.HALF_UP);String number="MC-"+DateTimeFormatter.BASIC_ISO_DATE.withZone(java.time.ZoneOffset.UTC).format(now)+"-"+orderId.toString().substring(0,8).toUpperCase();OrderEntity order=orders.save(new OrderEntity(orderId,number,userId,subtotal,coupon.discount(),total,currency,coupon.userCouponId(),now));List<OrderItemEntity> saved=quantities.entrySet().stream().map(e->{ProductEntity p=found.get(e.getKey());return new OrderItemEntity(orderId,p.getId(),p.getName(),p.getSku(),p.getPrice(),e.getValue());}).toList();items.saveAll(saved);outbox.append("ORDER",orderId.toString(),"order.created.v1",Map.of("orderId",orderId,"userId",userId,"total",total,"currency",currency,"traceId",String.valueOf(MDC.get("traceId"))));record.complete(orderId);audit.record(userId,"ORDER_CREATE","ORDER",orderId,null,Map.of("status",order.getStatus(),"total",total));metrics.counter("commerce.orders.created").increment();return OrderMapper.view(order,saved);}
 private SortedMap<Long,Integer> normalize(CreateOrderRequest r){if(r.items()==null||r.items().isEmpty())throw new BusinessException(ErrorCode.ORDER_EMPTY,"订单不能为空");SortedMap<Long,Integer> result=new TreeMap<>();for(OrderLineRequest line:r.items()){if(line==null||line.productId()==null||line.quantity()<=0)throw new BusinessException(ErrorCode.VALIDATION_ERROR,"商品和数量非法");result.merge(line.productId(),line.quantity(),Math::addExact);}return result;}
}
''',
"mini-commerce/backend/src/main/java/com/example/minicommerce/order/application/OrderCommandService.java": r'''package com.example.minicommerce.order.application;
import static com.example.minicommerce.order.api.OrderDtos.*;import com.example.minicommerce.audit.application.AuditService;import com.example.minicommerce.inventory.application.InventoryService;import com.example.minicommerce.messaging.application.OutboxService;import com.example.minicommerce.order.infrastructure.*;import com.example.minicommerce.promotion.application.CouponService;import com.example.minicommerce.shared.error.*;import com.example.minicommerce.shared.security.UserPrincipal;import java.time.Clock;import java.util.*;import java.util.stream.Collectors;import org.springframework.stereotype.Service;import org.springframework.transaction.annotation.Transactional;
@Service public class OrderCommandService{private final OrderRepository orders;private final OrderItemRepository items;private final InventoryService inventory;private final CouponService coupons;private final OutboxService outbox;private final OrderQueryService query;private final AuditService audit;private final Clock clock;public OrderCommandService(OrderRepository o,OrderItemRepository i,InventoryService inv,CouponService c,OutboxService out,OrderQueryService q,AuditService a,Clock clock){orders=o;items=i;inventory=inv;coupons=c;outbox=out;query=q;audit=a;this.clock=clock;}
 @Transactional public OrderResponse cancel(UUID id,UserPrincipal actor){OrderEntity order=orders.findForUpdate(id).orElseThrow(()->new BusinessException(ErrorCode.ORDER_NOT_FOUND,"订单不存在"));query.authorize(order,actor);String before=order.getStatus().name();order.cancel(clock.instant());List<OrderItemEntity> lines=items.findByOrderIdOrderById(id);Map<Long,Integer>qty=lines.stream().collect(Collectors.toMap(OrderItemEntity::getProductId,OrderItemEntity::getQuantity));inventory.release(qty);coupons.release(order.getUserCouponId(),id);outbox.append("ORDER",id.toString(),"order.cancelled.v1",Map.of("orderId",id,"userId",order.getUserId()));audit.record(actor.id(),"ORDER_CANCEL","ORDER",id,Map.of("status",before),Map.of("status",order.getStatus()));return OrderMapper.view(order,lines);}}
''',
"mini-commerce/backend/src/main/java/com/example/minicommerce/order/api/OrderController.java": r'''package com.example.minicommerce.order.api;
import static com.example.minicommerce.order.api.OrderDtos.*;import com.example.minicommerce.order.application.*;import com.example.minicommerce.shared.security.CurrentUser;import jakarta.validation.Valid;import java.util.UUID;import org.springframework.data.domain.*;import org.springframework.http.HttpStatus;import org.springframework.web.bind.annotation.*;
@RestController @RequestMapping("/api/orders")public class OrderController{private final CreateOrderService create;private final OrderCommandService commands;private final OrderQueryService query;private final CurrentUser current;public OrderController(CreateOrderService c,OrderCommandService cmd,OrderQueryService q,CurrentUser u){create=c;commands=cmd;query=q;current=u;}@PostMapping@ResponseStatus(HttpStatus.CREATED)public OrderResponse create(@RequestHeader("Idempotency-Key")String key,@Valid@RequestBody CreateOrderRequest r){return create.create(current.require().id(),key,r);}@GetMapping("/{id}")public OrderResponse get(@PathVariable UUID id){return query.get(id,current.require());}@GetMapping public Page<OrderResponse>list(@PageableDefault(size=20,sort="createdAt",direction=Sort.Direction.DESC)Pageable p){return query.list(current.require(),p);}@PostMapping("/{id}/cancellation")public OrderResponse cancel(@PathVariable UUID id){return commands.cancel(id,current.require());}}
'''
}
