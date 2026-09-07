package com.example.minicommerce.payment.domain;

/**
 * 支付尝试的状态：刚登记、处理中、成功、明确拒付、结果未知。
 *
 * <p><strong>作用：</strong>支付尝试的状态：刚登记、处理中、成功、明确拒付、结果未知。
 *
 * <p><strong>为什么：</strong>状态必须区分“失败”和“还不知道”；超时只能说明没有及时取得结果，不能证明没有扣款。
 *
 * <p><strong>对应文档：</strong> {@code 05_auth_security/03_Web常见攻击.md}、 {@code
 * 07_rabbitmq/04_幂等与Outbox.md}、 {@code 11_system_design/04_韧性_Timeout_Retry_Circuit.md}。
 */
public enum PaymentStatus {
    INITIATED,
    PROCESSING,
    SUCCEEDED,
    DECLINED,
    UNKNOWN
}
