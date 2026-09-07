package com.example.minicommerce.refund.infrastructure;

import jakarta.persistence.LockModeType;
import java.util.*;
import org.springframework.data.jpa.repository.*;
import org.springframework.data.repository.query.Param;

/**
 * refund模块的基础设施适配层：{@code RefundRepository}。
 *
 * <p><strong>作用：</strong>声明数据库查询或更新能力，由 Spring Data 创建实现；它不负责 Redis、RabbitMQ，也不决定整个业务流程。
 *
 * <p><strong>为什么：</strong>数据库表和框架会变化；隔离适配器可以避免这些变化扩散到业务规则和 API 契约。
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
