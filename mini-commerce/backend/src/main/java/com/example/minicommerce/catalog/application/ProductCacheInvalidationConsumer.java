package com.example.minicommerce.catalog.application;

import com.example.minicommerce.messaging.application.*;
import com.example.minicommerce.messaging.config.RabbitTopology;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.amqp.rabbit.annotation.RabbitListener;
import org.springframework.stereotype.Component;
import org.springframework.transaction.annotation.Transactional;

/**
 * 商品目录模块的应用用例编排层：{@code ProductCacheInvalidationConsumer}。
 *
 * <p><strong>作用：</strong>编排一个完整业务用例，协调领域规则、仓储、外部端口与事务边界。
 *
 * <p><strong>为什么：</strong>事务应该围绕业务动作，而不是分散在 Controller 或每个 Repository 中。
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
    @Transactional
    public void invalidate(String raw) throws Exception {
        EventEnvelope e = json.readValue(raw, EventEnvelope.class);
        if (!processed.claim("cache-product-changed", e.eventId())) return;
        cache.evict(e.payload().get("productId").asLong());
    }
}
