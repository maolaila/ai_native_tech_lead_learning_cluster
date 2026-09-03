package com.example.minicommerce.payment;

import static org.assertj.core.api.Assertions.*;

import com.example.minicommerce.payment.application.WebhookSignature;
import com.example.minicommerce.shared.config.AppProperties;
import com.example.minicommerce.shared.error.BusinessException;
import java.time.Duration;
import org.junit.jupiter.api.Test;

/**
 * 支付模块的自动化验证层：{@code WebhookSignatureTest}。
 *
 * <p><strong>作用：</strong>提供可重复的行为、数据、并发或故障证据，而不是只证明代码能够编译。
 *
 * <p><strong>为什么：</strong>历史规则和 Bug 只有进入自动化测试，才不会在后续重构或 AI 生成代码时悄悄回归。
 *
 * <p><strong>对应文档：</strong> {@code 05_auth_security/03_Web常见攻击.md}、 {@code
 * 07_rabbitmq/04_幂等与Outbox.md}、 {@code 11_system_design/04_韧性_Timeout_Retry_Circuit.md}。
 */
class WebhookSignatureTest {
    @Test
    void invalidSignature_isRejected() {
        AppProperties p =
                new AppProperties(
                        new AppProperties.Jwt(
                                "x",
                                "eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHg=",
                                Duration.ofMinutes(1),
                                Duration.ofDays(1)),
                        new AppProperties.Payment(
                                "secret", Duration.ofMillis(1), Duration.ofMillis(1)),
                        new AppProperties.Cache(
                                Duration.ofMinutes(1),
                                Duration.ofSeconds(1),
                                Duration.ofSeconds(1)),
                        new AppProperties.Outbox(
                                1,
                                Duration.ofSeconds(1),
                                Duration.ofSeconds(1),
                                Duration.ofSeconds(1)));
        WebhookSignature s = new WebhookSignature(p);
        assertThatThrownBy(() -> s.verify("{}", "00")).isInstanceOf(BusinessException.class);
    }
}
