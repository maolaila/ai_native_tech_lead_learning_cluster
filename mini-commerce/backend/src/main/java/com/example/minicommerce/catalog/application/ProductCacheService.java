package com.example.minicommerce.catalog.application;

import com.example.minicommerce.catalog.api.ProductDtos.ProductResponse;
import com.example.minicommerce.shared.config.AppProperties;
import com.example.minicommerce.shared.error.BusinessException;
import com.example.minicommerce.shared.error.ErrorCode;
import com.example.minicommerce.shared.redis.RedisLockService;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.time.Duration;
import java.util.Optional;
import java.util.concurrent.*;
import java.util.function.Supplier;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.stereotype.Service;

/**
 * 商品展示缓存：Cache Aside、短期空值缓存、TTL 抖动与受控回源。
 *
 * <p><strong>大白话：</strong>同一实例中同一商品只派一个请求查数据库，其他请求短暂等待同一结果。 最多同时回源 8 个不同商品；繁忙时返回 503，而不是把压力无限转给数据库。
 *
 * <p>Redis 锁是跨实例的尽力协调，不保证强一致；下单始终读取数据库权威价格。
 *
 * <p><strong>对应文档：</strong>{@code 06_redis/03_穿透_击穿_雪崩与一致性.md}。
 */
@Service
public class ProductCacheService {
    private static final Logger log = LoggerFactory.getLogger(ProductCacheService.class);
    private static final String NULL = "__NULL__";
    private final StringRedisTemplate redis;
    private final ObjectMapper json;
    private final AppProperties properties;
    private final RedisLockService locks;
    private final ConcurrentMap<Long, CompletableFuture<Optional<ProductResponse>>> flights =
            new ConcurrentHashMap<>();
    private final Semaphore databaseSlots = new Semaphore(8);

    public ProductCacheService(
            StringRedisTemplate redis,
            ObjectMapper json,
            AppProperties properties,
            RedisLockService locks) {
        this.redis = redis;
        this.json = json;
        this.properties = properties;
        this.locks = locks;
    }

    public Optional<ProductResponse> get(Long id, Supplier<Optional<ProductResponse>> loader) {
        String key = "product:v1:" + id;
        Optional<ProductResponse> cached = readCache(key);
        if (cached != null) return cached;
        CompletableFuture<Optional<ProductResponse>> mine = new CompletableFuture<>();
        CompletableFuture<Optional<ProductResponse>> existing = flights.putIfAbsent(id, mine);
        if (existing != null) return await(existing);
        boolean acquired = false;
        RedisLockService.LockHandle lock = null;
        try {
            acquired = databaseSlots.tryAcquire();
            if (!acquired) throw busy();
            cached = readCache(key);
            if (cached != null) {
                mine.complete(cached);
                return cached;
            }
            boolean redisAvailable = true;
            try {
                lock = locks.tryLock("lock:load:" + key, Duration.ofSeconds(3));
            } catch (RuntimeException cacheUnavailable) {
                redisAvailable = false;
            }
            // 别的实例正在回源时不绕过锁直接查数据库。Redis 故障时仍受本实例信号量限制。
            if (redisAvailable && lock == null) throw busy();
            Optional<ProductResponse> loaded = loader.get();
            writeCache(key, loaded);
            mine.complete(loaded);
            return loaded;
        } catch (RuntimeException | Error failure) {
            mine.completeExceptionally(failure);
            throw failure;
        } finally {
            if (lock != null) {
                try {
                    locks.release(lock);
                } catch (RuntimeException ignored) {
                    log.warn("event=cache_unlock_failed productId={}", id);
                }
            }
            if (acquired) databaseSlots.release();
            flights.remove(id, mine);
        }
    }

    private Optional<ProductResponse> await(CompletableFuture<Optional<ProductResponse>> existing) {
        try {
            return existing.get(2, TimeUnit.SECONDS);
        } catch (InterruptedException interrupted) {
            Thread.currentThread().interrupt();
            throw busy();
        } catch (TimeoutException timeout) {
            throw busy();
        } catch (ExecutionException failed) {
            if (failed.getCause() instanceof RuntimeException runtime) throw runtime;
            if (failed.getCause() instanceof Error error) throw error;
            throw new IllegalStateException("商品回源失败", failed.getCause());
        }
    }

    /** null 是未命中；Optional.empty 是确实查过但不存在，二者不能混淆。 */
    private Optional<ProductResponse> readCache(String key) {
        try {
            String raw = redis.opsForValue().get(key);
            if (raw == null) return null;
            if (NULL.equals(raw)) return Optional.empty();
            return Optional.of(json.readValue(raw, ProductResponse.class));
        } catch (RuntimeException | JsonProcessingException failed) {
            log.warn("event=cache_read_failed key={}", key);
            return null;
        }
    }

    private void writeCache(String key, Optional<ProductResponse> loaded) {
        try {
            if (loaded.isPresent()) {
                redis.opsForValue()
                        .set(
                                key,
                                json.writeValueAsString(loaded.get()),
                                jittered(properties.cache().productTtl()));
            } else {
                redis.opsForValue().set(key, NULL, properties.cache().nullTtl());
            }
        } catch (RuntimeException | JsonProcessingException failed) {
            // 数据库已经查完；写缓存失败不能再查一次，也不能把成功读取改成错误。
            log.warn("event=cache_write_failed key={}", key);
        }
    }

    public void evict(Long id) {
        try {
            redis.delete("product:v1:" + id);
        } catch (RuntimeException failed) {
            log.warn("event=product_cache_evict_failed productId={}", id);
        }
    }

    private BusinessException busy() {
        return new BusinessException(ErrorCode.DEPENDENCY_BUSY, "商品读取繁忙，请稍后重试");
    }

    private Duration jittered(Duration base) {
        long bound = Math.max(1, properties.cache().ttlJitter().toMillis());
        return base.plusMillis(ThreadLocalRandom.current().nextLong(bound));
    }
}
