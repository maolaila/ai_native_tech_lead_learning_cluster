package com.example.minicommerce.shared.config;

import java.time.Duration;
import org.springframework.boot.context.properties.ConfigurationProperties;

/**
 * 类型化配置集中定义外部可变参数，避免业务代码到处散落字符串形式的 @Value。
 * 对应文档：02_backend_spring/05_日志_配置与健康检查.md、08_runtime_deployment/03_配置_Secret与环境.md。
 */
@ConfigurationProperties(prefix = "app")
public record AppProperties(Jwt jwt, Payment payment, Cache cache, Outbox outbox) {
    public record Jwt(String issuer, String secret, Duration accessTtl, Duration refreshTtl) {}

    public record Payment(String webhookSecret, Duration connectTimeout, Duration readTimeout) {}

    public record Cache(Duration productTtl, Duration nullTtl, Duration ttlJitter) {}

    public record Outbox(
            int batchSize, Duration lease, Duration publishTimeout, Duration pollDelay) {}
}
