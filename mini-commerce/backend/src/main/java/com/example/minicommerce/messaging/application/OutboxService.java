package com.example.minicommerce.messaging.application;

import com.example.minicommerce.messaging.infrastructure.*;
import com.fasterxml.jackson.databind.*;
import java.time.Clock;
import java.util.*;
import org.slf4j.MDC;
import org.springframework.stereotype.Service;

/** 业务表与待发布事件在同一 PostgreSQL 事务中保存，闭合“数据库成功但消息没发”的双写空窗。 对应文档：07_rabbitmq/04_幂等与Outbox.md。 */
@Service
public class OutboxService {
    private final OutboxEventRepository repository;
    private final ObjectMapper json;
    private final Clock clock;

    public OutboxService(OutboxEventRepository r, ObjectMapper j, Clock c) {
        repository = r;
        json = j;
        clock = c;
    }

    public UUID append(String aggregateType, String aggregateId, String eventType, Object payload) {
        try {
            UUID id = UUID.randomUUID();
            EventEnvelope env =
                    new EventEnvelope(
                            id,
                            eventType,
                            1,
                            clock.instant(),
                            "mini-commerce",
                            aggregateType,
                            aggregateId,
                            MDC.get("traceId"),
                            json.valueToTree(payload));
            repository.save(
                    new OutboxEventEntity(
                            id,
                            aggregateType,
                            aggregateId,
                            eventType,
                            json.writeValueAsString(env),
                            clock.instant()));
            return id;
        } catch (Exception e) {
            throw new IllegalStateException("Outbox 序列化失败", e);
        }
    }
}
