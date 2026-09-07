package com.example.minicommerce.promotion.infrastructure;

import com.example.minicommerce.promotion.domain.UserCouponStatus;
import jakarta.persistence.*;
import java.util.UUID;

/**
 * 保存某个用户领到的券，以及它被哪张订单占用。
 *
 * <p><strong>作用：</strong>保存某个用户领到的券，以及它被哪张订单占用。
 *
 * <p><strong>为什么：</strong>reserve、markUsed、release 分别表示占用、用掉、退回。检查订单 ID，避免订单 A 释放订单 B 的券。
 *
 * <p><strong>对应文档：</strong> {@code 03_testing/02_测试用例设计.md}、 {@code
 * 04_database_postgresql/02_约束_范式与数据建模.md}。
 */
@Entity
@Table(
        name = "user_coupons",
        uniqueConstraints =
                @UniqueConstraint(
                        name = "ux_user_coupon",
                        columnNames = {"user_id", "coupon_id"}))
public class UserCouponEntity {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "user_id", nullable = false)
    private Long userId;

    @Column(name = "coupon_id", nullable = false)
    private Long couponId;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false, length = 20)
    private UserCouponStatus status;

    @Column(name = "reserved_order_id")
    private UUID reservedOrderId;

    @Version
    @Column(nullable = false)
    private long version;

    protected UserCouponEntity() {}

    public UserCouponEntity(Long u, Long c) {
        userId = u;
        couponId = c;
        status = UserCouponStatus.ISSUED;
    }

    public Long getId() {
        return id;
    }

    public Long getUserId() {
        return userId;
    }

    public Long getCouponId() {
        return couponId;
    }

    public UserCouponStatus getStatus() {
        return status;
    }

    public void reserve(UUID orderId) {
        if (status != UserCouponStatus.ISSUED) throw new IllegalStateException("coupon not issued");
        status = UserCouponStatus.RESERVED;
        reservedOrderId = orderId;
    }

    public void markUsed(UUID orderId) {
        if (status == UserCouponStatus.USED) return;
        if (status != UserCouponStatus.RESERVED || !orderId.equals(reservedOrderId))
            throw new IllegalStateException("coupon reservation mismatch");
        status = UserCouponStatus.USED;
    }

    public void release(UUID orderId) {
        if (status == UserCouponStatus.RESERVED && orderId.equals(reservedOrderId)) {
            status = UserCouponStatus.ISSUED;
            reservedOrderId = null;
        }
    }
}
