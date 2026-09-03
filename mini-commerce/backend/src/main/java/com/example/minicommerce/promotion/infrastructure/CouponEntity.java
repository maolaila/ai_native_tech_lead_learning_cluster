package com.example.minicommerce.promotion.infrastructure;

import com.example.minicommerce.promotion.domain.CouponType;
import jakarta.persistence.*;
import java.math.BigDecimal;
import java.time.Instant;

/**
 * 优惠券模块的基础设施适配层：{@code CouponEntity}。
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
