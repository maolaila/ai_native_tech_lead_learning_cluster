package com.example.minicommerce.refund.application;

import com.example.minicommerce.payment.application.PaymentGateway;
import com.example.minicommerce.shared.security.UserPrincipal;
import java.math.BigDecimal;
import java.util.UUID;
import org.springframework.stereotype.Service;

/**
 * 退款流程的三段式编排：短事务登记 → 事务外请求提供方 → 短事务保存结果。
 *
 * <p><strong>为什么拆成两个 Bean：</strong>同一个对象直接调用自己的 @Transactional 方法不会经过 Spring 代理。 本类调用独立的
 * RefundTransactionService，让事务真正生效，而不是只在方法上贴注解。
 *
 * <p>本项目只演示付款后的全额退款，不连接真实资金系统；UNKNOWN 必须核对，不能假定失败后再退款。
 *
 * <p><strong>对应文档：</strong>{@code 04_database_postgresql/04_事务与Spring边界.md}、 {@code
 * mini-commerce/docs/testing-strategy.md}。
 */
@Service
public class RefundService {
    private final RefundTransactionService transactions;
    private final PaymentGateway gateway;

    public RefundService(RefundTransactionService transactions, PaymentGateway gateway) {
        this.transactions = transactions;
        this.gateway = gateway;
    }

    public RefundView refund(UUID paymentId, UserPrincipal actor, String key) {
        RefundView refund = transactions.begin(paymentId, actor, key);
        if (!"INITIATED".equals(refund.status())) return refund;
        if (!transactions.claim(refund.refundId())) return transactions.get(refund.refundId());
        PaymentGateway.GatewayResult result;
        try {
            // refundId 是本次退款的稳定业务编号，重试时必须交给提供方去重。
            result = gateway.refund(refund.refundId(), paymentId, refund.amount());
        } catch (RuntimeException transportFailure) {
            result = PaymentGateway.GatewayResult.unknown("退款调用结果未知，需要核对原退款编号");
        }
        return transactions.finish(refund.refundId(), result);
    }

    public record RefundView(
            UUID refundId,
            UUID paymentId,
            UUID orderId,
            String status,
            BigDecimal amount,
            String providerReference,
            String error) {}
}
