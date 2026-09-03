package com.example.minicommerce.catalog.application;

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
 * Cache Aside：命中直接返回；Miss 查 PostgreSQL；不存在结果使用短 Null Cache；TTL 加抖动。 Redis 失败时商品读取可 Fail Open
 * 回源，但下单永远绕过缓存重新读取权威价格。 对应文档：06_redis/02_CacheAside_TTL与失效.md、06_redis/03_穿透_击穿_雪崩与一致性.md。
 */
@Service
public class ProductCacheService {
    private static final Logger log = LoggerFactory.getLogger(ProductCacheService.class);
    private static final String NULL = "__NULL__";
    private final StringRedisTemplate redis;
    private final ObjectMapper json;
    private final AppProperties properties;
    private final RedisLockService locks;

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
        try {
            Optional<ProductResponse> cached = decode(redis.opsForValue().get(key));
            if (cached != null) return cached;
            var lock = locks.tryLock("lock:load:" + key, Duration.ofSeconds(3));
            if (lock == null) return loader.get(); // 有其他请求回源时不无限等待，避免线程堆积。
            try {
                cached = decode(redis.opsForValue().get(key));
                if (cached != null) return cached;
                Optional<ProductResponse> loaded = loader.get();
                if (loaded.isPresent())
                    redis.opsForValue()
                            .set(
                                    key,
                                    json.writeValueAsString(loaded.get()),
                                    jittered(properties.cache().productTtl()));
                else redis.opsForValue().set(key, NULL, properties.cache().nullTtl());
                return loaded;
            } finally {
                locks.release(lock);
            }
        } catch (RuntimeException | JsonProcessingException ex) {
            log.warn(
                    "event=product_cache_failed productId={} reason={}",
                    id,
                    ex.getClass().getSimpleName());
            return loader.get();
        }
    }

    public void evict(Long id) {
        try {
            redis.delete("product:v1:" + id);
        } catch (RuntimeException ex) {
            log.warn("event=product_cache_evict_failed productId={}", id);
        }
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
