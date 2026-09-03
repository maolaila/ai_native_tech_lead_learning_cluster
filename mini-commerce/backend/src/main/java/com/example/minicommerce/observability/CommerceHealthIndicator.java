package com.example.minicommerce.observability;

import org.springframework.boot.actuate.health.*;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Component;

/**
 * Readiness 检查权威 PostgreSQL；Redis 缓存故障不会让 Liveness 失败并触发所有实例重启。
 *
 * <p><strong>对应文档：</strong> {@code 10_observability/01_结构化日志与关联ID.md}、 {@code
 * 10_observability/02_Metrics_RED_USE与百分位.md}、 {@code 10_observability/03_Tracing与上下文传播.md}。
 */
@Component("commerceDatabase")
public class CommerceHealthIndicator implements HealthIndicator {
    private final JdbcTemplate jdbc;

    public CommerceHealthIndicator(JdbcTemplate j) {
        jdbc = j;
    }

    public Health health() {
        try {
            Integer one = jdbc.queryForObject("select 1", Integer.class);
            return Health.up().withDetail("database", one).build();
        } catch (Exception e) {
            return Health.down(e).build();
        }
    }
}
