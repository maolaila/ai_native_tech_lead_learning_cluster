package com.example.minicommerce.payment.infrastructure;

import jakarta.persistence.LockModeType;
import java.time.Instant;
import java.util.*;
import org.springframework.data.jpa.repository.*;
import org.springframework.data.repository.query.Param;

/**
 * 查询支付记录、加行锁，以及竞争一次支付的执行权。
 *
 * <p><strong>作用：</strong>查询支付记录、加行锁，以及竞争一次支付的执行权。
 *
 * <p><strong>为什么：</strong>claim 用条件更新把 INITIATED 或过期的 PROCESSING 改成处理中；不同请求不能同时拿到同一次执行权。
 *
 * <p><strong>对应文档：</strong> {@code 05_auth_security/03_Web常见攻击.md}、 {@code
 * 07_rabbitmq/04_幂等与Outbox.md}、 {@code 11_system_design/04_韧性_Timeout_Retry_Circuit.md}。
 */
public interface PaymentAttemptRepository extends JpaRepository<PaymentAttemptEntity, UUID> {
    Optional<PaymentAttemptEntity> findByUserIdAndIdempotencyKey(Long userId, String key);

    // 在订单行锁保护下查询；UNKNOWN 不是失败，不能另开一笔支付。
    boolean existsByOrderIdAndStatusNot(
            UUID orderId, com.example.minicommerce.payment.domain.PaymentStatus status);

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
