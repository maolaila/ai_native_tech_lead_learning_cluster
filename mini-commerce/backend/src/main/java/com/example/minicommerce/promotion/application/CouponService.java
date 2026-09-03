package com.example.minicommerce.promotion.application;

import com.example.minicommerce.promotion.domain.*;
import com.example.minicommerce.promotion.infrastructure.*;
import com.example.minicommerce.shared.error.*;
import java.math.*;
import java.time.Clock;
import java.util.*;
import org.springframework.stereotype.Service;

/** 对应文档：03_testing/02_测试用例设计.md。最低金额、有效期、归属和一次性使用都在服务端验证。 */
@Service
public class CouponService {
    private final CouponRepository coupons;
    private final UserCouponRepository userCoupons;
    private final Clock clock;

    public CouponService(CouponRepository c, UserCouponRepository u, Clock clock) {
        coupons = c;
        userCoupons = u;
        this.clock = clock;
    }

    public CouponReservation reserve(String code, Long userId, BigDecimal subtotal, UUID orderId) {
        if (code == null || code.isBlank()) return CouponReservation.none();
        CouponEntity c =
                coupons.findByCodeIgnoreCase(code.trim())
                        .orElseThrow(
                                () -> new BusinessException(ErrorCode.COUPON_NOT_FOUND, "优惠券不存在"));
        if (!c.validAt(clock.instant()) || subtotal.compareTo(c.getMinAmount()) < 0)
            throw new BusinessException(ErrorCode.COUPON_NOT_APPLICABLE, "优惠券不可用");
        UserCouponEntity uc =
                userCoupons
                        .findForUpdate(userId, c.getId())
                        .orElseThrow(
                                () ->
                                        new BusinessException(
                                                ErrorCode.COUPON_NOT_APPLICABLE, "优惠券不属于当前用户"));
        if (uc.getStatus() != UserCouponStatus.ISSUED)
            throw new BusinessException(ErrorCode.COUPON_ALREADY_USED, "优惠券已使用或被占用");
        BigDecimal discount =
                c.getType() == CouponType.PERCENT
                        ? subtotal.multiply(c.getValue())
                                .divide(BigDecimal.valueOf(100), 2, RoundingMode.HALF_UP)
                        : c.getValue();
        if (c.getMaxDiscount() != null && discount.compareTo(c.getMaxDiscount()) > 0)
            discount = c.getMaxDiscount();
        if (discount.compareTo(subtotal) > 0) discount = subtotal;
        uc.reserve(orderId);
        return new CouponReservation(uc.getId(), discount.setScale(2, RoundingMode.HALF_UP));
    }

    public void markUsed(Long id, UUID orderId) {
        if (id != null) userCoupons.findById(id).orElseThrow().markUsed(orderId);
    }

    public void release(Long id, UUID orderId) {
        if (id != null) userCoupons.findById(id).ifPresent(c -> c.release(orderId));
    }

    public record CouponReservation(Long userCouponId, BigDecimal discount) {
        public static CouponReservation none() {
            return new CouponReservation(null, BigDecimal.ZERO.setScale(2));
        }
    }
}
