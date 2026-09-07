package com.example.minicommerce.payment.application;

import com.example.minicommerce.audit.application.AuditService;
import com.example.minicommerce.inventory.application.InventoryService;
import com.example.minicommerce.messaging.application.OutboxService;
import com.example.minicommerce.order.application.*;
import com.example.minicommerce.order.domain.OrderStatus;
import com.example.minicommerce.order.infrastructure.*;
import com.example.minicommerce.payment.domain.PaymentStatus;
import com.example.minicommerce.payment.infrastructure.*;
import com.example.minicommerce.promotion.application.CouponService;
import com.example.minicommerce.shared.error.*;
import com.example.minicommerce.shared.security.UserPrincipal;
import java.nio.charset.StandardCharsets;
import java.security.*;
import java.time.Clock;
import java.util.*;
import java.util.stream.Collectors;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

/**
 * 支付 API 幂等先于订单当前状态判断，因此客户端在成功响应丢失后重试，仍能得到第一次结果。
 *
 * <p><strong>对应文档：</strong> {@code 05_auth_security/03_Web常见攻击.md}、 {@code
 * 07_rabbitmq/04_幂等与Outbox.md}、 {@code 11_system_design/04_韧性_Timeout_Retry_Circuit.md}。
 */
@Service
public class PaymentTransactionService {
    private final PaymentAttemptRepository payments;
    private final OrderRepository orders;
    private final OrderItemRepository items;
    private final OrderQueryService query;
    private final InventoryService inventory;
    private final CouponService coupons;
    private final OutboxService outbox;
    private final AuditService audit;
    private final Clock clock;
    private final IdempotencyLock idempotencyLock;

    public PaymentTransactionService(
            PaymentAttemptRepository p,
            OrderRepository o,
            OrderItemRepository i,
            OrderQueryService q,
            InventoryService inv,
            CouponService c,
            OutboxService out,
            AuditService a,
            Clock clock,
            IdempotencyLock idempotencyLock) {
        payments = p;
        orders = o;
        items = i;
        query = q;
        inventory = inv;
        coupons = c;
        outbox = out;
        audit = a;
        this.clock = clock;
        this.idempotencyLock = idempotencyLock;
    }

    @Transactional
    public PaymentView createOrGet(
            UUID orderId, UserPrincipal actor, String key, String paymentToken) {
        if (key == null || key.isBlank())
            throw new BusinessException(
                    ErrorCode.IDEMPOTENCY_KEY_REQUIRED, "支付必须提供 Idempotency-Key");
        if (key.length() > 128 || paymentToken == null || paymentToken.isBlank()) {
            throw new BusinessException(ErrorCode.VALIDATION_ERROR, "支付参数非法，幂等键最长 128 字符");
        }
        // 同一用户的相同键先串行；数据库唯一约束是最后防线，不是正常重试流程。
        idempotencyLock.acquire("payment:" + actor.id() + ":" + key);
        String hash = hash(orderId + ":" + paymentToken);
        Optional<PaymentAttemptEntity> prior =
                payments.findByUserIdAndIdempotencyKey(actor.id(), key);
        if (prior.isPresent()) {
            PaymentAttemptEntity p = prior.get();
            if (!p.getRequestHash().equals(hash) || !p.getOrderId().equals(orderId))
                throw new BusinessException(ErrorCode.IDEMPOTENCY_CONFLICT, "同一支付幂等键请求不同");
            return view(p);
        }
        OrderEntity order =
                orders.findForUpdate(orderId)
                        .orElseThrow(
                                () -> new BusinessException(ErrorCode.ORDER_NOT_FOUND, "订单不存在"));
        query.authorizeWrite(order, actor);
        if (!order.getUserId().equals(actor.id())) {
            throw new BusinessException(ErrorCode.ACCESS_DENIED, "只能为自己的订单创建支付");
        }
        if (order.getStatus() != OrderStatus.PENDING_PAYMENT)
            throw new BusinessException(ErrorCode.ORDER_NOT_PAYABLE, "订单不可支付");
        if (payments.existsByOrderIdAndStatusNot(orderId, PaymentStatus.DECLINED)) {
            throw new BusinessException(
                    ErrorCode.PAYMENT_IN_PROGRESS, "订单已有支付记录，请使用原幂等键查询或等待核对，不能用新键重复扣款");
        }
        PaymentAttemptEntity p =
                payments.saveAndFlush(
                        new PaymentAttemptEntity(
                                UUID.randomUUID(),
                                orderId,
                                actor.id(),
                                key,
                                hash,
                                order.getTotalAmount(),
                                order.getCurrency(),
                                clock.instant()));
        return view(p);
    }

    @Transactional
    public boolean claim(UUID paymentId) {
        return payments.claim(paymentId, clock.instant().minusSeconds(120)) == 1;
    }

    @Transactional
    public PaymentView apply(UUID paymentId, PaymentGateway.GatewayResult result) {
        PaymentAttemptEntity p = payments.findForUpdate(paymentId).orElseThrow();
        if (p.getStatus() == PaymentStatus.SUCCEEDED || p.getStatus() == PaymentStatus.DECLINED)
            return view(p);
        if (result.success()) {
            OrderEntity order = orders.findForUpdate(p.getOrderId()).orElseThrow();
            if (order.markPaid(p.getId(), clock.instant())) {
                Map<Long, Integer> qty =
                        items.findByOrderIdOrderById(order.getId()).stream()
                                .collect(
                                        Collectors.toMap(
                                                OrderItemEntity::getProductId,
                                                OrderItemEntity::getQuantity));
                inventory.confirmSale(qty);
                coupons.markUsed(order.getUserCouponId(), order.getId());
                outbox.append(
                        "ORDER",
                        order.getId().toString(),
                        "order.paid.v1",
                        Map.of(
                                "orderId",
                                order.getId(),
                                "userId",
                                order.getUserId(),
                                "total",
                                order.getTotalAmount(),
                                "currency",
                                order.getCurrency()));
            }
            p.succeeded(result.reference(), clock.instant());
            audit.record(
                    p.getUserId(),
                    "PAYMENT_SUCCEEDED",
                    "PAYMENT",
                    p.getId(),
                    null,
                    Map.of("orderId", p.getOrderId(), "providerReference", result.reference()));
        } else if (result.unknown()) p.unknown(result.error(), clock.instant());
        else p.declined(result.error(), clock.instant());
        return view(p);
    }

    @Transactional(readOnly = true)
    public PaymentView get(UUID id, UserPrincipal actor) {
        PaymentAttemptEntity p = payments.findById(id).orElseThrow();
        if (!p.getUserId().equals(actor.id())
                && !actor.role().name().equals("ADMIN")
                && !actor.role().name().equals("SUPPORT"))
            throw new BusinessException(ErrorCode.ACCESS_DENIED, "不能读取他人的支付");
        return view(p);
    }

    private String hash(String s) {
        try {
            return HexFormat.of()
                    .formatHex(
                            MessageDigest.getInstance("SHA-256")
                                    .digest(s.getBytes(StandardCharsets.UTF_8)));
        } catch (Exception e) {
            throw new IllegalStateException(e);
        }
    }

    public static PaymentView view(PaymentAttemptEntity p) {
        return new PaymentView(
                p.getId(),
                p.getOrderId(),
                p.getStatus().name(),
                p.getAmount(),
                p.getCurrency(),
                p.getProviderReference(),
                p.getLastError());
    }

    public record PaymentView(
            UUID paymentId,
            UUID orderId,
            String status,
            java.math.BigDecimal amount,
            String currency,
            String providerReference,
            String error) {}
}
