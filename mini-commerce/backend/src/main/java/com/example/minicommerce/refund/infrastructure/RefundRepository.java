package com.example.minicommerce.refund.infrastructure;

import jakarta.persistence.LockModeType;
import java.util.*;
import org.springframework.data.jpa.repository.*;
import org.springframework.data.repository.query.Param;

/**
 * 按支付和幂等键查退款，并能锁住一条退款记录。
 *
 * <p><strong>作用：</strong>按支付和幂等键查退款，并能锁住一条退款记录。
 *
 * <p><strong>为什么：</strong>重试需要找回原退款；数据库另限制同一笔支付只能有一条未明确失败的退款，避免重复退钱。
 *
 * <p><strong>对应文档：</strong> {@code 02_backend_spring/01_请求生命周期与IoC_DI.md}、 {@code
 * 02_backend_spring/04_API设计_校验_异常与错误码.md}、 {@code 11_system_design/02_模块化单体与边界.md}。
 */
public interface RefundRepository extends JpaRepository<RefundEntity, UUID> {
    Optional<RefundEntity> findByPaymentIdAndKey(UUID paymentId, String key);

    boolean existsByPaymentIdAndStatusNot(UUID paymentId, String status);

    @Lock(LockModeType.PESSIMISTIC_WRITE)
    @Query("select r from RefundEntity r where r.id=:id")
    Optional<RefundEntity> findForUpdate(@Param("id") UUID id);
}
