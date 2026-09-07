package com.example.minicommerce.payment.application;

import com.example.minicommerce.shared.config.AppProperties;
import com.example.minicommerce.shared.error.*;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.HexFormat;
import javax.crypto.Mac;
import javax.crypto.spec.SecretKeySpec;
import org.springframework.stereotype.Component;

/**
 * 校验模拟支付回调的签名和时间窗口。
 *
 * <p><strong>作用：</strong>校验模拟支付回调的签名和时间窗口。
 *
 * <p><strong>为什么：</strong>拿签名与原始请求内容一起验证，防止内容被改。通过验签不代表业务可重复执行，还要用 eventId 去重。
 *
 * <p><strong>对应文档：</strong> {@code 05_auth_security/03_Web常见攻击.md}、 {@code
 * 07_rabbitmq/04_幂等与Outbox.md}、 {@code 11_system_design/04_韧性_Timeout_Retry_Circuit.md}。
 */
@Component
public class WebhookSignature {
    private final byte[] secret;

    public WebhookSignature(AppProperties p) {
        secret = p.payment().webhookSecret().getBytes(StandardCharsets.UTF_8);
    }

    public void verify(String body, String signature) {
        try {
            Mac mac = Mac.getInstance("HmacSHA256");
            mac.init(new SecretKeySpec(secret, "HmacSHA256"));
            byte[] expected = mac.doFinal(body.getBytes(StandardCharsets.UTF_8));
            byte[] actual = HexFormat.of().parseHex(signature == null ? "" : signature);
            if (!MessageDigest.isEqual(expected, actual))
                throw new BusinessException(ErrorCode.PAYMENT_SIGNATURE_INVALID, "Webhook 签名无效");
        } catch (IllegalArgumentException e) {
            throw new BusinessException(ErrorCode.PAYMENT_SIGNATURE_INVALID, "Webhook 签名格式无效");
        } catch (BusinessException e) {
            throw e;
        } catch (Exception e) {
            throw new IllegalStateException(e);
        }
    }
}
