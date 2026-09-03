package com.example.minicommerce.promotion.infrastructure;
import java.util.Optional;import org.springframework.data.jpa.repository.*;import org.springframework.data.repository.query.Param;import jakarta.persistence.LockModeType;
public interface UserCouponRepository extends JpaRepository<UserCouponEntity,Long>{@Lock(LockModeType.PESSIMISTIC_WRITE)@Query("select u from UserCouponEntity u where u.userId=:userId and u.couponId=:couponId")Optional<UserCouponEntity> findForUpdate(@Param("userId")Long userId,@Param("couponId")Long couponId);}
