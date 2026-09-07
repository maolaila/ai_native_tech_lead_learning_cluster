package com.example.minicommerce.refund.application;

import com.example.minicommerce.messaging.application.OutboxService;
import com.example.minicommerce.order.application.OrderQueryService;
import com.example.minicommerce.order.infrastructure.*;
import com.example.minicommerce.payment.application.*;
import com.example.minicommerce.payment.infrastructure.*;
import com.example.minicommerce.refund.application.RefundService.RefundView;
import com.example.minicommerce.refund.infrastructure.*;
import com.example.minicommerce.shared.error.*;
import com.example.minicommerce.shared.security.UserPrincipal;
import java.time.Clock;
import java.util.*;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

/**
 * 用短数据库事务登记退款、领取执行权、保存退款结果。
 *
 * <p><strong>作用：</strong>用短数据库事务登记退款、领取执行权、保存退款结果。
 *
 * <p><strong>为什么：</strong>真正调用支付方在 RefundService 中进行。拆成两个 Spring 对象，使调用经过事务代理，而不是同一对象自己调用自己。
 *
 * <p><strong>对应文档：</strong> {@code 02_backend_spring/01_请求生命周期与IoC_DI.md}、 {@code
 * 02_backend_spring/04_API设计_校验_异常与错误码.md}、 {@code 11_system_design/02_模块化单体与边界.md}。
 */
@Service
public class RefundTransactionService {
    private final RefundRepository refunds;
    private final PaymentAttemptRepository payments;
    private final OrderRepository orders;
    private final OrderQueryService query;
    private final OutboxService outbox;
    private final Clock clock;

    public RefundTransactionService(
            RefundRepository r,
            PaymentAttemptRepository p,
            OrderRepository o,
            OrderQueryService q,
            OutboxService out,
            Clock c) {
        refunds = r;
        payments = p;
        orders = o;
        query = q;
        outbox = out;
        clock = c;
    }

    @Transactional
    public RefundView begin(UUID paymentId, UserPrincipal actor, String key) {
        if (key == null || key.isBlank())
            throw new BusinessException(
                    ErrorCode.IDEMPOTENCY_KEY_REQUIRED, "退款必须提供 Idempotency-Key");
        if (key.length() > 128) {
            throw new BusinessException(ErrorCode.VALIDATION_ERROR, "退款幂等键最长 128 字符");
        }
        PaymentAttemptEntity payment =
                payments.findForUpdate(paymentId)
                        .orElseThrow(
                                () ->
                                        new BusinessException(
                                                ErrorCode.ORDER_NOT_REFUNDABLE, "支付不存在"));
        if (!payment.getUserId().equals(actor.id()) && !actor.role().name().equals("ADMIN"))
            throw new BusinessException(ErrorCode.ACCESS_DENIED, "不能退款他人的订单");
        // 先授权再查重：幂等重放也不能泄露他人的退款结果。
        Optional<RefundEntity> prior = refunds.findByPaymentIdAndKey(paymentId, key);
        if (prior.isPresent()) return view(prior.get());
        if (refunds.existsByPaymentIdAndStatusNot(paymentId, "FAILED")) {
            throw new BusinessException(ErrorCode.ORDER_NOT_REFUNDABLE, "已有退款记录，请使用原键核对结果");
        }
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

    /** 领取执行权；并发重试只有一个请求能把 INITIATED 改为 PROCESSING。 */
    @Transactional
    public boolean claim(UUID id) {
        RefundEntity refund = refunds.findForUpdate(id).orElseThrow();
        return refund.claim(clock.instant());
    }

    @Transactional(readOnly = true)
    public RefundView get(UUID id) {
        return view(refunds.findById(id).orElseThrow());
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
}
