package com.example.minicommerce.refund.application;

import com.example.minicommerce.messaging.application.OutboxService;
import com.example.minicommerce.order.application.OrderQueryService;
import com.example.minicommerce.order.infrastructure.*;
import com.example.minicommerce.payment.application.*;
import com.example.minicommerce.payment.infrastructure.*;
import com.example.minicommerce.refund.infrastructure.*;
import com.example.minicommerce.shared.error.*;
import com.example.minicommerce.shared.security.UserPrincipal;
import java.time.Clock;
import java.util.*;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

/**
 * refund模块的应用用例编排层：{@code RefundService}。
 *
 * <p><strong>作用：</strong>编排一个完整业务用例，协调领域规则、仓储、外部端口与事务边界。
 *
 * <p><strong>为什么：</strong>事务应该围绕业务动作，而不是分散在 Controller 或每个 Repository 中。
 *
 * <p><strong>对应文档：</strong> {@code 02_backend_spring/01_请求生命周期与IoC_DI.md}、 {@code
 * 02_backend_spring/04_API设计_校验_异常与错误码.md}、 {@code 11_system_design/02_模块化单体与边界.md}。
 */
@Service
public class RefundService {
    private final RefundRepository refunds;
    private final PaymentAttemptRepository payments;
    private final OrderRepository orders;
    private final OrderQueryService query;
    private final PaymentGateway gateway;
    private final OutboxService outbox;
    private final Clock clock;

    public RefundService(
            RefundRepository r,
            PaymentAttemptRepository p,
            OrderRepository o,
            OrderQueryService q,
            PaymentGateway g,
            OutboxService out,
            Clock c) {
        refunds = r;
        payments = p;
        orders = o;
        query = q;
        gateway = g;
        outbox = out;
        clock = c;
    }

    public RefundView refund(UUID paymentId, UserPrincipal actor, String key) {
        RefundView begun = begin(paymentId, actor, key);
        if (!"INITIATED".equals(begun.status())) return begun;
        PaymentGateway.GatewayResult result = gateway.refund(paymentId, begun.amount());
        return finish(begun.refundId(), result);
    }

    @Transactional
    public RefundView begin(UUID paymentId, UserPrincipal actor, String key) {
        if (key == null || key.isBlank())
            throw new BusinessException(
                    ErrorCode.IDEMPOTENCY_KEY_REQUIRED, "退款必须提供 Idempotency-Key");
        Optional<RefundEntity> prior = refunds.findByPaymentIdAndKey(paymentId, key);
        if (prior.isPresent()) return view(prior.get());
        PaymentAttemptEntity payment =
                payments.findForUpdate(paymentId)
                        .orElseThrow(
                                () ->
                                        new BusinessException(
                                                ErrorCode.ORDER_NOT_REFUNDABLE, "支付不存在"));
        if (!payment.getUserId().equals(actor.id()) && !actor.role().name().equals("ADMIN"))
            throw new BusinessException(ErrorCode.ACCESS_DENIED, "不能退款他人的订单");
        if (payment.getStatus() != com.example.minicommerce.payment.domain.PaymentStatus.SUCCEEDED)
            throw new BusinessException(ErrorCode.ORDER_NOT_REFUNDABLE, "支付未成功");
        OrderEntity order = orders.findForUpdate(payment.getOrderId()).orElseThrow();
        query.authorize(order, actor);
        order.requestRefund(clock.instant());
        return view(
                refunds.save(
                        new RefundEntity(
                                paymentId,
                                order.getId(),
                                actor.id(),
                                key,
                                payment.getAmount(),
                                clock.instant())));
    }

    @Transactional
    public RefundView finish(UUID id, PaymentGateway.GatewayResult result) {
        RefundEntity refund = refunds.findForUpdate(id).orElseThrow();
        OrderEntity order = orders.findForUpdate(refund.getOrderId()).orElseThrow();
        if ("SUCCEEDED".equals(refund.getStatus()) || "FAILED".equals(refund.getStatus()))
            return view(refund);
        if (result.success()) {
            refund.success(result.reference(), clock.instant());
            order.markRefunded(clock.instant());
            outbox.append(
                    "ORDER",
                    order.getId().toString(),
                    "order.refunded.v1",
                    Map.of(
                            "orderId",
                            order.getId(),
                            "userId",
                            order.getUserId(),
                            "amount",
                            refund.getAmount()));
        } else if (result.unknown()) refund.unknown(result.error(), clock.instant());
        else {
            refund.failed(result.error(), clock.instant());
            order.refundFailed(clock.instant());
        }
        return view(refund);
    }

    private static RefundView view(RefundEntity r) {
        return new RefundView(
                r.getId(),
                r.getPaymentId(),
                r.getOrderId(),
                r.getStatus(),
                r.getAmount(),
                r.getProviderReference(),
                r.getLastError());
    }

    public record RefundView(
            UUID refundId,
            UUID paymentId,
            UUID orderId,
            String status,
            java.math.BigDecimal amount,
            String providerReference,
            String error) {}
}
