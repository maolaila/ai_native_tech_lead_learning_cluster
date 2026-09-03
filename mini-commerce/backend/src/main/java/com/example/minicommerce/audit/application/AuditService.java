package com.example.minicommerce.audit.application;

import com.example.minicommerce.audit.infrastructure.*;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.time.Clock;
import org.slf4j.MDC;
import org.springframework.stereotype.Service;

/**
 * 审计回答“谁在何时改了什么”，与可采样、可轮转的普通应用日志职责不同。
 * 对应文档：02_backend_spring/05_日志_配置与健康检查.md、10_observability/01_结构化日志与关联ID.md。
 */
@Service
public class AuditService {
    private final AuditLogRepository repository;
    private final ObjectMapper json;
    private final Clock clock;
    public AuditService(AuditLogRepository repository, ObjectMapper json, Clock clock) {
        this.repository=repository; this.json=json; this.clock=clock;
    }
    public void record(Long actorId, String action, String type, Object id, Object before, Object after) {
        repository.save(new AuditLogEntity(actorId, action, type, String.valueOf(id), "SUCCESS", MDC.get("traceId"),
            serialize(before), serialize(after), clock.instant()));
    }
    private String serialize(Object value) {
        if (value == null) return null;
        try { return json.writeValueAsString(value); }
        catch (JsonProcessingException e) { return "{\"serializationError\":true}"; }
    }
}
