package com.example.minicommerce.payment.api;

import com.example.minicommerce.payment.application.*;
import com.example.minicommerce.payment.application.PaymentTransactionService.PaymentView;
import com.example.minicommerce.refund.application.RefundService;
import com.example.minicommerce.refund.application.RefundService.RefundView;
import com.example.minicommerce.shared.security.CurrentUser;
import jakarta.validation.Valid;
import jakarta.validation.constraints.NotBlank;
import java.util.UUID;
import org.springframework.web.bind.annotation.*;

/**
 * 支付模块的HTTP/API 适配层：{@code PaymentController}。
 *
 * <p><strong>作用：</strong>负责路由、请求参数、校验、认证主体和 HTTP 响应转换，不承载核心业务规则。
 *
 * <p><strong>为什么：</strong>把 HTTP 细节留在系统边界，应用服务才能脱离 Web 框架测试和复用。
 *
 * <p><strong>对应文档：</strong> {@code 05_auth_security/03_Web常见攻击.md}、 {@code
 * 07_rabbitmq/04_幂等与Outbox.md}、 {@code 11_system_design/04_韧性_Timeout_Retry_Circuit.md}。
 */
@RestController
@RequestMapping("/api/payments")
public class PaymentController {
    private final PaymentOrchestrator payments;
    private final PaymentWebhookService webhooks;
    private final RefundService refunds;
    private final CurrentUser current;

    public PaymentController(
            PaymentOrchestrator p, PaymentWebhookService w, RefundService r, CurrentUser c) {
        payments = p;
        webhooks = w;
        refunds = r;
        current = c;
    }

    @PostMapping("/orders/{orderId}")
    public PaymentView pay(
            @PathVariable UUID orderId,
            @RequestHeader("Idempotency-Key") String key,
            @Valid @RequestBody PayRequest request) {
        return payments.pay(orderId, current.require(), key, request.paymentToken());
    }

    @PostMapping("/{paymentId}/refunds")
    public RefundView refund(
            @PathVariable UUID paymentId, @RequestHeader("Idempotency-Key") String key) {
        return refunds.refund(paymentId, current.require(), key);
    }

    @PostMapping("/webhooks/fake")
    public void webhook(
            @RequestHeader(value = "X-Payment-Signature", required = false) String signature,
            @RequestBody String body)
            throws Exception {
        webhooks.handle(body, signature);
    }

    public record PayRequest(@NotBlank String paymentToken) {}
}
