package com.example.minicommerce.messaging.application;
import com.fasterxml.jackson.databind.JsonNode;import java.time.Instant;import java.util.UUID;
/** 消息是跨时间 API，因此显式携带 eventId、schemaVersion、发生时间、聚合标识和 traceId。 */
public record EventEnvelope(UUID eventId,String eventType,int schemaVersion,Instant occurredAt,String producer,String aggregateType,String aggregateId,String traceId,JsonNode payload){}
