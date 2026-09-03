package com.example.minicommerce.payment.domain;

/**
 * 支付模块的领域模型层：{@code PaymentStatus}。
 *
 * <p><strong>作用：</strong>表达业务状态、行为和不变量，并尽量保持对 Spring、HTTP 与数据库实现无感。
 *
 * <p><strong>为什么：</strong>领域方法比任意 Setter 更能阻止非法状态，也使测试直接描述业务语言。
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
