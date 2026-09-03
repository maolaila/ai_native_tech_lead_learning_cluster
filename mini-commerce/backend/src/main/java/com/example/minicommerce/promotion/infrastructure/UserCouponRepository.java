package com.example.minicommerce.promotion.infrastructure;

import jakarta.persistence.LockModeType;
import java.util.Optional;
import org.springframework.data.jpa.repository.*;
import org.springframework.data.repository.query.Param;

/**
 * 优惠券模块的基础设施适配层：{@code UserCouponRepository}。
 *
 * <p><strong>作用：</strong>负责 JPA、SQL、Redis、RabbitMQ 或外部系统等技术实现，并把技术细节隔离在业务边界之外。
 *
 * <p><strong>为什么：</strong>数据库表和框架会变化；隔离适配器可以避免这些变化扩散到业务规则和 API 契约。
 *
 * <p><strong>对应文档：</strong> {@code 03_testing/02_测试用例设计.md}、 {@code
 * 04_database_postgresql/02_约束_范式与数据建模.md}。
 */
public interface UserCouponRepository extends JpaRepository<UserCouponEntity, Long> {
    @Lock(LockModeType.PESSIMISTIC_WRITE)
    @Query("select u from UserCouponEntity u where u.userId=:userId and u.couponId=:couponId")
    Optional<UserCouponEntity> findForUpdate(
            @Param("userId") Long userId, @Param("couponId") Long couponId);
}
