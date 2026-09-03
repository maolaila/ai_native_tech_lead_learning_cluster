from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
PROJECT = REPO / "mini-commerce"


def write(relative: str, content: str) -> None:
    path = REPO / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


write("mini-commerce/backend/src/main/java/com/example/minicommerce/messaging/config/RabbitTopology.java", r'''package com.example.minicommerce.messaging.config;

import org.springframework.amqp.core.*;
import org.springframework.amqp.rabbit.core.RabbitTemplate;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.boot.ApplicationRunner;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

/**
 * 每种业务订阅者使用独立 Queue；同 Queue 的多个实例才是水平竞争消费。
 * 所有已发布的 order.* 事件都有审计订阅，Mandatory Return 不会把合法事件误判为未路由。
 */
@Configuration
public class RabbitTopology {
    public static final String EVENTS = "commerce.events";
    public static final String DLX = "commerce.dlx";
    public static final String NOTIFICATION_Q = "notification.order-paid.v1";
    public static final String POINTS_Q = "points.order-paid.v1";
    public static final String CACHE_Q = "cache.product-changed.v1";
    public static final String AUDIT_Q = "audit.order-events.v1";

    @Bean("commerceExchange") TopicExchange commerceExchange() { return new TopicExchange(EVENTS, true, false); }
    @Bean("deadLetterExchange") DirectExchange deadLetterExchange() { return new DirectExchange(DLX, true, false); }

    private Queue durable(String name) {
        return QueueBuilder.durable(name).deadLetterExchange(DLX).deadLetterRoutingKey(name + ".dead").build();
    }

    @Bean("notificationQueue") Queue notificationQueue() { return durable(NOTIFICATION_Q); }
    @Bean("pointsQueue") Queue pointsQueue() { return durable(POINTS_Q); }
    @Bean("cacheQueue") Queue cacheQueue() { return durable(CACHE_Q); }
    @Bean("auditQueue") Queue auditQueue() { return durable(AUDIT_Q); }
    @Bean("notificationDlq") Queue notificationDlq() { return QueueBuilder.durable(NOTIFICATION_Q + ".dlq").build(); }
    @Bean("pointsDlq") Queue pointsDlq() { return QueueBuilder.durable(POINTS_Q + ".dlq").build(); }
    @Bean("cacheDlq") Queue cacheDlq() { return QueueBuilder.durable(CACHE_Q + ".dlq").build(); }
    @Bean("auditDlq") Queue auditDlq() { return QueueBuilder.durable(AUDIT_Q + ".dlq").build(); }

    @Bean Binding notificationBinding(@Qualifier("notificationQueue") Queue queue,
                                      @Qualifier("commerceExchange") TopicExchange exchange) {
        return BindingBuilder.bind(queue).to(exchange).with("order.paid.v1");
    }
    @Bean Binding pointsBinding(@Qualifier("pointsQueue") Queue queue,
                                @Qualifier("commerceExchange") TopicExchange exchange) {
        return BindingBuilder.bind(queue).to(exchange).with("order.paid.v1");
    }
    @Bean Binding cacheBinding(@Qualifier("cacheQueue") Queue queue,
                               @Qualifier("commerceExchange") TopicExchange exchange) {
        return BindingBuilder.bind(queue).to(exchange).with("product.changed.v1");
    }
    @Bean Binding auditBinding(@Qualifier("auditQueue") Queue queue,
                               @Qualifier("commerceExchange") TopicExchange exchange) {
        return BindingBuilder.bind(queue).to(exchange).with("order.#");
    }
    @Bean Binding notificationDead(@Qualifier("notificationDlq") Queue queue,
                                   @Qualifier("deadLetterExchange") DirectExchange exchange) {
        return BindingBuilder.bind(queue).to(exchange).with(NOTIFICATION_Q + ".dead");
    }
    @Bean Binding pointsDead(@Qualifier("pointsDlq") Queue queue,
                             @Qualifier("deadLetterExchange") DirectExchange exchange) {
        return BindingBuilder.bind(queue).to(exchange).with(POINTS_Q + ".dead");
    }
    @Bean Binding cacheDead(@Qualifier("cacheDlq") Queue queue,
                            @Qualifier("deadLetterExchange") DirectExchange exchange) {
        return BindingBuilder.bind(queue).to(exchange).with(CACHE_Q + ".dead");
    }
    @Bean Binding auditDead(@Qualifier("auditDlq") Queue queue,
                            @Qualifier("deadLetterExchange") DirectExchange exchange) {
        return BindingBuilder.bind(queue).to(exchange).with(AUDIT_Q + ".dead");
    }

    @Bean
    ApplicationRunner requireRoutableReturns(RabbitTemplate template) {
        return args -> template.setMandatory(true);
    }
}
''')

write("mini-commerce/backend/src/main/java/com/example/minicommerce/audit/application/OrderCreatedAuditConsumer.java", r'''package com.example.minicommerce.audit.application;

import com.example.minicommerce.messaging.application.EventEnvelope;
import com.example.minicommerce.messaging.application.ProcessedMessageService;
import com.example.minicommerce.messaging.config.RabbitTopology;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.util.UUID;
import org.springframework.amqp.rabbit.annotation.RabbitListener;
import org.springframework.stereotype.Component;
import org.springframework.transaction.annotation.Transactional;

/** 所有订单事件的审计订阅者；事件类型本身成为可搜索的审计 Action。 */
@Component
public class OrderCreatedAuditConsumer {
    private final ObjectMapper json;
    private final ProcessedMessageService processed;
    private final AuditService audit;

    public OrderCreatedAuditConsumer(ObjectMapper json, ProcessedMessageService processed, AuditService audit) {
        this.json = json;
        this.processed = processed;
        this.audit = audit;
    }

    @RabbitListener(queues = RabbitTopology.AUDIT_Q)
    @Transactional
    public void consume(String raw) throws Exception {
        EventEnvelope event = json.readValue(raw, EventEnvelope.class);
        if (!processed.claim("audit-order-events", event.eventId())) return;
        Long userId = event.payload().hasNonNull("userId") ? event.payload().get("userId").asLong() : null;
        audit.record(userId, "EVENT_" + event.eventType().toUpperCase().replace('.', '_'), "ORDER",
            UUID.fromString(event.aggregateId()), null, event.payload());
    }
}
''')

# OncePerRequestFilter 作为 Spring Bean 时会被 Servlet 容器自动注册；显式关闭，保证只在 Security Chain 中执行一次。
write("mini-commerce/backend/src/main/java/com/example/minicommerce/shared/security/SecurityFilterRegistration.java", r'''package com.example.minicommerce.shared.security;

import com.example.minicommerce.shared.web.RateLimitFilter;
import org.springframework.boot.web.servlet.FilterRegistrationBean;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class SecurityFilterRegistration {
    @Bean
    FilterRegistrationBean<JwtAuthenticationFilter> disableJwtServletAutoRegistration(JwtAuthenticationFilter filter) {
        FilterRegistrationBean<JwtAuthenticationFilter> registration = new FilterRegistrationBean<>(filter);
        registration.setEnabled(false);
        return registration;
    }

    @Bean
    FilterRegistrationBean<RateLimitFilter> disableRateLimitServletAutoRegistration(RateLimitFilter filter) {
        FilterRegistrationBean<RateLimitFilter> registration = new FilterRegistrationBean<>(filter);
        registration.setEnabled(false);
        return registration;
    }
}
''')

# 一条命令重建最终工程；它是补丁链的稳定入口，便于以后更新文档后重新生成映射。
write("tools/regenerate_complete_project.py", r'''from __future__ import annotations
import subprocess
import sys
from pathlib import Path

repo = Path(__file__).resolve().parents[1]
scripts = [
    "tools/generate_complete_mini_commerce_v2.py",
    "tools/apply_final_fixes_v2.py",
    "tools/apply_release_fixes_v2.py",
    "tools/apply_completeness_fixes_v3.py",
    "tools/apply_ci_and_docs_fixes_v5.py",
    "tools/apply_runtime_and_gate_fixes_v6.py",
    "tools/apply_release_cleanup_v7.py",
    "tools/refine_document_mapping_v3.py",
    "tools/finalize_delivery_v7.py",
]
for script in scripts:
    if script.endswith("apply_release_cleanup_v7.py") and Path(sys.argv[0]).name == Path(script).name:
        continue
    subprocess.run([sys.executable, script], cwd=repo, check=True)
print("完整工程已重新生成；仍需运行 CI/Make test 才能证明运行时正确。")
''')

# 删除一次性生成和发布工作流；最终 main 只保留持续质量门禁 mini-commerce-ci.yml。
obsolete = [
    ".github/workflows/generate-complete-mini-commerce.yml",
    ".github/workflows/validate-and-promote-mini-commerce.yml",
    ".github/workflows/validate-and-promote-mini-commerce-v2.yml",
    ".github/workflows/validate-and-promote-mini-commerce-v3.yml",
    ".github/workflows/validate-and-promote-mini-commerce-v4.yml",
    ".github/workflows/validate-and-promote-mini-commerce-v5.yml",
    ".github/workflows/bootstrap-complete-mini-commerce.yml",
    ".github/workflows/bootstrap-complete-mini-commerce-v6.yml",
]
for relative in obsolete:
    path = REPO / relative
    if path.exists(): path.unlink()

print(json.dumps({"status": "release-cleanup-v7-applied", "removedWorkflows": obsolete}, ensure_ascii=False))
