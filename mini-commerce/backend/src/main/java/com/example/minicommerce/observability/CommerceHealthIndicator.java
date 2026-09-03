package com.example.minicommerce.observability;
import org.springframework.jdbc.core.JdbcTemplate;import org.springframework.boot.actuate.health.*;import org.springframework.stereotype.Component;
/** Readiness 检查权威 PostgreSQL；Redis 缓存故障不会让 Liveness 失败并触发所有实例重启。 */
@Component("commerceDatabase")public class CommerceHealthIndicator implements HealthIndicator{private final JdbcTemplate jdbc;public CommerceHealthIndicator(JdbcTemplate j){jdbc=j;}public Health health(){try{Integer one=jdbc.queryForObject("select 1",Integer.class);return Health.up().withDetail("database",one).build();}catch(Exception e){return Health.down(e).build();}}}
