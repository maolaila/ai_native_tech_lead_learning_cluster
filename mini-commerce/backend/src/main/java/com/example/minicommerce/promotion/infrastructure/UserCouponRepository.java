package com.example.minicommerce.promotion.infrastructure;

import jakarta.persistence.LockModeType;
import java.util.Optional;
import org.springframework.data.jpa.repository.*;
import org.springframework.data.repository.query.Param;

/**
 * 查找发给某个用户的某张优惠券，并可锁住这条领券记录。
 *
 * <p><strong>作用：</strong>查找发给某个用户的某张优惠券，并可锁住这条领券记录。
 *
 * <p><strong>为什么：</strong>优惠券模板和个人领取记录不同；锁住个人记录，是为了避免两张订单同时占用同一张券。
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
