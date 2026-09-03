package com.example.minicommerce.payment.application;

import java.math.BigDecimal;
import java.util.UUID;

/**
 * 外部支付是不可由数据库事务回滚的 Port，因此调用必须放在短数据库事务之外。
 *
 * <p><strong>对应文档：</strong> {@code 05_auth_security/03_Web常见攻击.md}、 {@code
 * 07_rabbitmq/04_幂等与Outbox.md}、 {@code 11_system_design/04_韧性_Timeout_Retry_Circuit.md}。
 */
public interface PaymentGateway {
    GatewayResult charge(UUID paymentId, BigDecimal amount, String currency, String paymentToken);

    GatewayResult refund(UUID paymentId, BigDecimal amount);

    record GatewayResult(boolean success, boolean unknown, String reference, String error) {
        public static GatewayResult success(String ref) {
            return new GatewayResult(true, false, ref, null);
        }

        public static GatewayResult declined(String e) {
            return new GatewayResult(false, false, null, e);
        }

        public static GatewayResult unknown(String e) {
            return new GatewayResult(false, true, null, e);
        }
    }
}
