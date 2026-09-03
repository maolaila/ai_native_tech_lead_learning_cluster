from __future__ import annotations

import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
PROJECT = REPO / "mini-commerce"


def write(relative: str, content: str) -> None:
    path = REPO / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


# 1. 相同订单幂等键若存在已提交的 PROCESSING 记录，明确返回冲突，而不是再次插入触发不透明 Unique 异常。
create_order = PROJECT / "backend/src/main/java/com/example/minicommerce/order/application/CreateOrderService.java"
text = create_order.read_text(encoding="utf-8")
old = 'if(prior.isPresent()){IdempotencyRecordEntity r=prior.get();if(!r.getRequestHash().equals(hash))throw new BusinessException(ErrorCode.IDEMPOTENCY_CONFLICT,"同一幂等键不能用于不同请求");if("COMPLETED".equals(r.getStatus()))return query.view(orders.findById(r.getResourceId()).orElseThrow());}'
new = 'if(prior.isPresent()){IdempotencyRecordEntity r=prior.get();if(!r.getRequestHash().equals(hash))throw new BusinessException(ErrorCode.IDEMPOTENCY_CONFLICT,"同一幂等键不能用于不同请求");if("COMPLETED".equals(r.getStatus()))return query.view(orders.findById(r.getResourceId()).orElseThrow());throw new BusinessException(ErrorCode.IDEMPOTENCY_CONFLICT,"相同请求正在处理，请稍后使用同一幂等键重试");}'
if old not in text:
    raise SystemExit("CreateOrderService 幂等补丁目标不存在")
create_order.write_text(text.replace(old, new), encoding="utf-8")

# 2. PostgreSQL char(3) 与 JPA varchar(3) 类型保持一致，避免 ddl-auto=validate 因 bpchar/varchar 差异失败。
migration = PROJECT / "backend/src/main/resources/db/migration/V001__baseline.sql"
migration.write_text(migration.read_text(encoding="utf-8").replace("char(3)", "varchar(3)"), encoding="utf-8")

# 3. 退款拆为事务服务和事务外编排器，避免同类自调用让 @Transactional 失效，也避免网络调用占用数据库锁。
old_refund = PROJECT / "backend/src/main/java/com/example/minicommerce/refund/application/RefundService.java"
if old_refund.exists():
    old_refund.unlink()

write("mini-commerce/backend/src/main/java/com/example/minicommerce/refund/application/RefundTransactionService.java", r'''package com.example.minicommerce.refund.application;

import com.example.minicommerce.messaging.application.OutboxService;
import com.example.minicommerce.order.application.OrderQueryService;
import com.example.minicommerce.order.infrastructure.OrderEntity;
import com.example.minicommerce.order.infrastructure.OrderRepository;
import com.example.minicommerce.payment.application.PaymentGateway;
import com.example.minicommerce.payment.domain.PaymentStatus;
import com.example.minicommerce.payment.infrastructure.PaymentAttemptEntity;
import com.example.minicommerce.payment.infrastructure.PaymentAttemptRepository;
import com.example.minicommerce.refund.infrastructure.RefundEntity;
import com.example.minicommerce.refund.infrastructure.RefundRepository;
import com.example.minicommerce.shared.error.BusinessException;
import com.example.minicommerce.shared.error.ErrorCode;
import com.example.minicommerce.shared.security.UserPrincipal;
import java.time.Clock;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

/**
 * 退款的两个短事务：begin 只校验并登记退款意图；finish 根据不可回滚的外部结果更新订单。
 * 对应文档：04_database_postgresql/04_事务与Spring边界.md、11_system_design/04_韧性_Timeout_Retry_Circuit.md。
 */
@Service
public class RefundTransactionService {
    private final RefundRepository refunds;
    private final PaymentAttemptRepository payments;
    private final OrderRepository orders;
    private final OrderQueryService orderQuery;
    private final OutboxService outbox;
    private final Clock clock;

    public RefundTransactionService(RefundRepository refunds, PaymentAttemptRepository payments, OrderRepository orders,
                                    OrderQueryService orderQuery, OutboxService outbox, Clock clock) {
        this.refunds = refunds;
        this.payments = payments;
        this.orders = orders;
        this.orderQuery = orderQuery;
        this.outbox = outbox;
        this.clock = clock;
    }

    @Transactional
    public RefundView begin(UUID paymentId, UserPrincipal actor, String idempotencyKey) {
        if (idempotencyKey == null || idempotencyKey.isBlank()) {
            throw new BusinessException(ErrorCode.IDEMPOTENCY_KEY_REQUIRED, "退款必须提供 Idempotency-Key");
        }
        Optional<RefundEntity> prior = refunds.findByPaymentIdAndKey(paymentId, idempotencyKey);
        if (prior.isPresent()) return view(prior.get());

        PaymentAttemptEntity payment = payments.findForUpdate(paymentId)
            .orElseThrow(() -> new BusinessException(ErrorCode.ORDER_NOT_REFUNDABLE, "支付不存在"));
        if (!payment.getUserId().equals(actor.id()) && !actor.role().name().equals("ADMIN")) {
            throw new BusinessException(ErrorCode.ACCESS_DENIED, "不能退款他人的订单");
        }
        if (payment.getStatus() != PaymentStatus.SUCCEEDED) {
            throw new BusinessException(ErrorCode.ORDER_NOT_REFUNDABLE, "支付尚未成功");
        }

        OrderEntity order = orders.findForUpdate(payment.getOrderId()).orElseThrow();
        orderQuery.authorize(order, actor);
        order.requestRefund(clock.instant());
        return view(refunds.save(new RefundEntity(paymentId, order.getId(), actor.id(), idempotencyKey,
            payment.getAmount(), clock.instant())));
    }

    @Transactional
    public RefundView finish(UUID refundId, PaymentGateway.GatewayResult result) {
        RefundEntity refund = refunds.findForUpdate(refundId).orElseThrow();
        OrderEntity order = orders.findForUpdate(refund.getOrderId()).orElseThrow();
        if ("SUCCEEDED".equals(refund.getStatus()) || "FAILED".equals(refund.getStatus())) return view(refund);

        if (result.success()) {
            refund.success(result.reference(), clock.instant());
            order.markRefunded(clock.instant());
            outbox.append("ORDER", order.getId().toString(), "order.refunded.v1", Map.of(
                "orderId", order.getId(), "userId", order.getUserId(), "amount", refund.getAmount()));
        } else if (result.unknown()) {
            // 响应丢失不能武断回到 PAID；保持 UNKNOWN/REFUNDING，等待查询或 Webhook 对账。
            refund.unknown(result.error(), clock.instant());
        } else {
            refund.failed(result.error(), clock.instant());
            order.refundFailed(clock.instant());
        }
        return view(refund);
    }

    private static RefundView view(RefundEntity refund) {
        return new RefundView(refund.getId(), refund.getPaymentId(), refund.getOrderId(), refund.getStatus(),
            refund.getAmount(), refund.getProviderReference(), refund.getLastError());
    }

    public record RefundView(UUID refundId, UUID paymentId, UUID orderId, String status,
                             java.math.BigDecimal amount, String providerReference, String error) {}
}
''')

write("mini-commerce/backend/src/main/java/com/example/minicommerce/refund/application/RefundOrchestrator.java", r'''package com.example.minicommerce.refund.application;

import com.example.minicommerce.payment.application.PaymentGateway;
import com.example.minicommerce.refund.application.RefundTransactionService.RefundView;
import com.example.minicommerce.shared.security.UserPrincipal;
import java.util.UUID;
import org.springframework.stereotype.Service;

/** 外部退款位于数据库事务外；事务不能回滚已经发送到支付机构的资金指令。 */
@Service
public class RefundOrchestrator {
    private final RefundTransactionService transactions;
    private final PaymentGateway gateway;

    public RefundOrchestrator(RefundTransactionService transactions, PaymentGateway gateway) {
        this.transactions = transactions;
        this.gateway = gateway;
    }

    public RefundView refund(UUID paymentId, UserPrincipal actor, String idempotencyKey) {
        RefundView intent = transactions.begin(paymentId, actor, idempotencyKey);
        if (!"INITIATED".equals(intent.status())) return intent;
        PaymentGateway.GatewayResult result = gateway.refund(paymentId, intent.amount());
        return transactions.finish(intent.refundId(), result);
    }
}
''')

write("mini-commerce/backend/src/main/java/com/example/minicommerce/payment/api/PaymentController.java", r'''package com.example.minicommerce.payment.api;

import com.example.minicommerce.payment.application.PaymentOrchestrator;
import com.example.minicommerce.payment.application.PaymentTransactionService.PaymentView;
import com.example.minicommerce.payment.application.PaymentWebhookService;
import com.example.minicommerce.refund.application.RefundOrchestrator;
import com.example.minicommerce.refund.application.RefundTransactionService.RefundView;
import com.example.minicommerce.shared.security.CurrentUser;
import jakarta.validation.Valid;
import jakarta.validation.constraints.NotBlank;
import java.util.UUID;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/payments")
public class PaymentController {
    private final PaymentOrchestrator payments;
    private final PaymentWebhookService webhooks;
    private final RefundOrchestrator refunds;
    private final CurrentUser currentUser;

    public PaymentController(PaymentOrchestrator payments, PaymentWebhookService webhooks,
                             RefundOrchestrator refunds, CurrentUser currentUser) {
        this.payments = payments;
        this.webhooks = webhooks;
        this.refunds = refunds;
        this.currentUser = currentUser;
    }

    @PostMapping("/orders/{orderId}")
    public PaymentView pay(@PathVariable UUID orderId, @RequestHeader("Idempotency-Key") String key,
                           @Valid @RequestBody PayRequest request) {
        return payments.pay(orderId, currentUser.require(), key, request.paymentToken());
    }

    @PostMapping("/{paymentId}/refunds")
    public RefundView refund(@PathVariable UUID paymentId, @RequestHeader("Idempotency-Key") String key) {
        return refunds.refund(paymentId, currentUser.require(), key);
    }

    @PostMapping("/webhooks/fake")
    public void webhook(@RequestHeader(value = "X-Payment-Signature", required = false) String signature,
                        @RequestBody String body) throws Exception {
        webhooks.handle(body, signature);
    }

    public record PayRequest(@NotBlank String paymentToken) {}
}
''')

# 4. 学习环境关闭 NAT 时，让 Fargate 使用公有子网和公有 IP；启用 NAT 后回到私有子网。
aws_main = PROJECT / "infra/aws/terraform/main.tf"
aws_text = aws_main.read_text(encoding="utf-8")
old_network = 'network_configuration { subnets = values(aws_subnet.private)[*].id; security_groups = [aws_security_group.app.id]; assign_public_ip = false }'
new_network = '''network_configuration {
    subnets          = var.enable_nat_gateway ? values(aws_subnet.private)[*].id : values(aws_subnet.public)[*].id
    security_groups  = [aws_security_group.app.id]
    assign_public_ip = var.enable_nat_gateway ? false : true
  }'''
if old_network not in aws_text:
    raise SystemExit("AWS ECS network 补丁目标不存在")
aws_main.write_text(aws_text.replace(old_network, new_network), encoding="utf-8")

# 5. py_compile 产生的缓存不得进入交付清单或 Git。
for cache in PROJECT.rglob("__pycache__"):
    if cache.is_dir():
        shutil.rmtree(cache)

# 6. 重新生成最终清单，确保只统计真正可提交文件。
files = [p for p in PROJECT.rglob("*") if p.is_file() and "target" not in p.parts and "__pycache__" not in p.parts]
hashes = {p.relative_to(PROJECT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(files)}
manifest = {
    "generatedAt": datetime.now(timezone.utc).isoformat(),
    "fileCount": len(files),
    "javaMainFiles": len(list((PROJECT / "backend/src/main/java").rglob("*.java"))),
    "javaTestFiles": len(list((PROJECT / "backend/src/test/java").rglob("*.java"))),
    "migrations": sorted(p.name for p in (PROJECT / "backend/src/main/resources/db/migration").glob("*.sql")),
    "sha256": hashes,
}
(PROJECT / "DELIVERY-MANIFEST.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"status": "final-fixes-applied", "files": len(files), "java": manifest["javaMainFiles"] + manifest["javaTestFiles"]}, ensure_ascii=False))
