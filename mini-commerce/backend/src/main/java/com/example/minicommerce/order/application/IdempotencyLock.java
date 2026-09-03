package com.example.minicommerce.order.application;

import java.sql.PreparedStatement;
import org.springframework.jdbc.core.*;
import org.springframework.stereotype.Component;

/**
 * PostgreSQL 事务级 advisory lock 只串行化“同一用户+同一幂等键”。第二个并发请求等待后会看到第一个已提交结果。
 * 对应文档：03_testing/06_API与契约测试.md、07_rabbitmq/04_幂等与Outbox.md。
 */
@Component
public class IdempotencyLock {
    private final JdbcTemplate jdbc;

    public IdempotencyLock(JdbcTemplate jdbc) {
        this.jdbc = jdbc;
    }

    public void acquire(String key) {
        jdbc.execute(
                (ConnectionCallback<Void>)
                        c -> {
                            try (PreparedStatement ps =
                                    c.prepareStatement(
                                            "select pg_advisory_xact_lock(hashtextextended(?,0))")) {
                                ps.setString(1, key);
                                ps.execute();
                                return null;
                            }
                        });
    }
}
