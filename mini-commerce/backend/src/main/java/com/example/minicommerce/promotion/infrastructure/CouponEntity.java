package com.example.minicommerce.promotion.infrastructure;

import com.example.minicommerce.promotion.domain.CouponType;
import jakarta.persistence.*;
import java.math.BigDecimal;
import java.time.Instant;

/**
 * 保存优惠券模板：券码、折扣方式、最低消费、封顶金额和有效期。
 *
 * <p><strong>作用：</strong>保存优惠券模板：券码、折扣方式、最低消费、封顶金额和有效期。
 *
 * <p><strong>为什么：</strong>一张模板可发给不同用户；哪个用户已经占用或使用，由 UserCouponEntity 记录。
 *
 * <p><strong>对应文档：</strong> {@code 03_testing/02_测试用例设计.md}、 {@code
 * 04_database_postgresql/02_约束_范式与数据建模.md}。
 */
@Entity
@Table(
        name = "coupons",
        indexes = @Index(name = "ux_coupon_code", columnList = "code", unique = true))
public class CouponEntity {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, length = 50)
    private String code;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false, length = 20)
    private CouponType type;

    @Column(nullable = false, precision = 19, scale = 2)
    private BigDecimal value;

    @Column(name = "min_amount", nullable = false, precision = 19, scale = 2)
    private BigDecimal minAmount;

    @Column(name = "max_discount", precision = 19, scale = 2)
    private BigDecimal maxDiscount;

    @Column(name = "valid_from", nullable = false)
    private Instant validFrom;

    @Column(name = "valid_until", nullable = false)
    private Instant validUntil;

    @Column(nullable = false)
    private boolean active;

    protected CouponEntity() {}

    public CouponEntity(
            String c,
            CouponType t,
            BigDecimal v,
            BigDecimal m,
            BigDecimal max,
            Instant from,
            Instant until) {
        code = c;
        type = t;
        value = v;
        minAmount = m;
        maxDiscount = max;
        validFrom = from;
        validUntil = until;
        active = true;
    }

    public Long getId() {
        return id;
    }

    public String getCode() {
        return code;
    }

    public CouponType getType() {
        return type;
    }

    public BigDecimal getValue() {
        return value;
    }

    public BigDecimal getMinAmount() {
        return minAmount;
    }

    public BigDecimal getMaxDiscount() {
        return maxDiscount;
    }

    public boolean validAt(Instant n) {
        return active && !n.isBefore(validFrom) && n.isBefore(validUntil);
    }
}
