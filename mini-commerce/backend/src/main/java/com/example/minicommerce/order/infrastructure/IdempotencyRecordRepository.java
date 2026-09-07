package com.example.minicommerce.order.infrastructure;

import java.util.*;
import org.springframework.data.jpa.repository.JpaRepository;

/**
 * 按用户 ID 与幂等键查找已经登记的下单请求。
 *
 * <p><strong>作用：</strong>按用户 ID 与幂等键查找已经登记的下单请求。
 *
 * <p><strong>为什么：</strong>不同用户可使用同一字符串键，因此不能只按 key 查询。数据库唯一约束和事务锁共同保护并发下单。
 *
 * <p><strong>对应文档：</strong> {@code 02_backend_spring/06_订单模块案例.md}、 {@code
 * 04_database_postgresql/04_事务与Spring边界.md}、 {@code 07_rabbitmq/04_幂等与Outbox.md}。
 */
public interface IdempotencyRecordRepository extends JpaRepository<IdempotencyRecordEntity, UUID> {
    Optional<IdempotencyRecordEntity> findByUserIdAndKey(Long userId, String key);
}
