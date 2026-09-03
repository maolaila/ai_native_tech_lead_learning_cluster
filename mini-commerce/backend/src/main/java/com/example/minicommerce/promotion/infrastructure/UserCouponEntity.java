package com.example.minicommerce.promotion.infrastructure;

import com.example.minicommerce.promotion.domain.UserCouponStatus;
import jakarta.persistence.*;
import java.util.UUID;

/**
 * 优惠券模块的基础设施适配层：{@code UserCouponEntity}。
 *
 * <p><strong>作用：</strong>负责 JPA、SQL、Redis、RabbitMQ 或外部系统等技术实现，并把技术细节隔离在业务边界之外。
 *
 * <p><strong>为什么：</strong>数据库表和框架会变化；隔离适配器可以避免这些变化扩散到业务规则和 API 契约。
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
