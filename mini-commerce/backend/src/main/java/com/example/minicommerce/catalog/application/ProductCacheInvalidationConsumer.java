package com.example.minicommerce.catalog.application;

import com.example.minicommerce.messaging.application.*;
import com.example.minicommerce.messaging.config.RabbitTopology;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.amqp.rabbit.annotation.RabbitListener;
import org.springframework.stereotype.Component;
import org.springframework.transaction.annotation.Transactional;

/**
 * 收到商品变更事件后，删除对应商品的 Redis 展示缓存。
 *
 * <p><strong>作用：</strong>收到商品变更事件后，删除对应商品的 Redis 展示缓存。
 *
 * <p><strong>为什么：</strong>下一次查询再加载数据库新值。重复删同一个缓存键无害，但删除失败不能声称已经获得强一致性。
 *
 * <p><strong>对应文档：</strong> {@code 02_backend_spring/03_DTO_Entity_Domain与映射.md}、 {@code
 * 06_redis/02_CacheAside_TTL与失效.md}。
 */
@Component
public class ProductCacheInvalidationConsumer {
    private final ObjectMapper json;
    private final ProcessedMessageService processed;
    private final ProductCacheService cache;

    public ProductCacheInvalidationConsumer(
            ObjectMapper j, ProcessedMessageService p, ProductCacheService c) {
        json = j;
        processed = p;
        cache = c;
    }

    @RabbitListener(queues = RabbitTopology.CACHE_Q)
    @Transactional(rollbackFor = Exception.class)
    public void invalidate(String raw) throws Exception {
        EventEnvelope e = json.readValue(raw, EventEnvelope.class);
        if (!processed.claim("cache-product-changed", e.eventId())) return;
        cache.evict(e.payload().get("productId").asLong());
    }
}
