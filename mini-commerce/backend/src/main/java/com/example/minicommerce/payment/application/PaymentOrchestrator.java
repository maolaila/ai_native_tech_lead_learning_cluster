package com.example.minicommerce.payment.application;

import com.example.minicommerce.payment.application.PaymentTransactionService.PaymentView;
import com.example.minicommerce.shared.security.UserPrincipal;
import java.util.UUID;
import org.springframework.stereotype.Service;

/**
 * 三段式边界：短事务建意图 → 事务外调用外部支付 → 短事务落结果。避免长事务持锁等待网络。
 *
 * <p><strong>对应文档：</strong> {@code 05_auth_security/03_Web常见攻击.md}、 {@code
 * 07_rabbitmq/04_幂等与Outbox.md}、 {@code 11_system_design/04_韧性_Timeout_Retry_Circuit.md}。
 */
@Service
public class PaymentOrchestrator {
    private final PaymentTransactionService tx;
    private final PaymentGateway gateway;

    public PaymentOrchestrator(PaymentTransactionService tx, PaymentGateway gateway) {
        this.tx = tx;
        this.gateway = gateway;
    }

    public PaymentView pay(UUID orderId, UserPrincipal actor, String key, String token) {
        PaymentView p = tx.createOrGet(orderId, actor, key, token);
        if (!"INITIATED".equals(p.status()) && !"PROCESSING".equals(p.status())) return p;
        if (!tx.claim(p.paymentId())) return tx.get(p.paymentId(), actor);
        PaymentGateway.GatewayResult result =
                gateway.charge(p.paymentId(), p.amount(), p.currency(), token);
        return tx.apply(p.paymentId(), result);
    }
}
