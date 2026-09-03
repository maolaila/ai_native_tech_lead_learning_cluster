package com.example.minicommerce.payment.infrastructure;

import jakarta.persistence.LockModeType;
import java.time.Instant;
import java.util.*;
import org.springframework.data.jpa.repository.*;
import org.springframework.data.repository.query.Param;

/**
 * 支付模块的基础设施适配层：{@code PaymentAttemptRepository}。
 *
 * <p><strong>作用：</strong>负责 JPA、SQL、Redis、RabbitMQ 或外部系统等技术实现，并把技术细节隔离在业务边界之外。
 *
 * <p><strong>为什么：</strong>数据库表和框架会变化；隔离适配器可以避免这些变化扩散到业务规则和 API 契约。
 *
 * <p><strong>对应文档：</strong> {@code 05_auth_security/03_Web常见攻击.md}、 {@code
 * 07_rabbitmq/04_幂等与Outbox.md}、 {@code 11_system_design/04_韧性_Timeout_Retry_Circuit.md}。
 */
public interface PaymentAttemptRepository extends JpaRepository<PaymentAttemptEntity, UUID> {
    Optional<PaymentAttemptEntity> findByUserIdAndIdempotencyKey(Long userId, String key);

    @Lock(LockModeType.PESSIMISTIC_WRITE)
    @Query("select p from PaymentAttemptEntity p where p.id=:id")
    Optional<PaymentAttemptEntity> findForUpdate(@Param("id") UUID id);

    @Modifying
    @Query(
            value =
                    "update payment_attempts set status='PROCESSING',processing_started_at=now(),updated_at=now(),version=version+1 where id=:id and (status='INITIATED' or (status='PROCESSING' and processing_started_at<:stale))",
            nativeQuery = true)
    int claim(@Param("id") UUID id, @Param("stale") Instant stale);
}
