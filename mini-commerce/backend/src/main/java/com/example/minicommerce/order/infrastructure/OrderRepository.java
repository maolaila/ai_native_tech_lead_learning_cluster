package com.example.minicommerce.order.infrastructure;

import jakarta.persistence.LockModeType;
import java.util.*;
import org.springframework.data.domain.*;
import org.springframework.data.jpa.repository.*;
import org.springframework.data.repository.query.Param;

/**
 * 查询订单、按用户分页，并在修改订单前锁住订单行。
 *
 * <p><strong>作用：</strong>查询订单、按用户分页，并在修改订单前锁住订单行。
 *
 * <p><strong>为什么：</strong>取消与支付可能同时发生；先锁住同一订单，再判断状态，避免双方都依据过期状态继续执行。
 *
 * <p><strong>对应文档：</strong> {@code 02_backend_spring/06_订单模块案例.md}、 {@code
 * 04_database_postgresql/04_事务与Spring边界.md}、 {@code 07_rabbitmq/04_幂等与Outbox.md}。
 */
public interface OrderRepository extends JpaRepository<OrderEntity, UUID> {
    @Lock(LockModeType.PESSIMISTIC_WRITE)
    @Query("select o from OrderEntity o where o.id=:id")
    Optional<OrderEntity> findForUpdate(@Param("id") UUID id);

    Page<OrderEntity> findByUserId(Long userId, Pageable pageable);
}
