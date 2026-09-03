from __future__ import annotations

import hashlib
import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
PROJECT = REPO / "mini-commerce"


def write(relative: str, content: str) -> None:
    path = REPO / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


write("mini-commerce/backend/src/main/java/com/example/minicommerce/order/application/OrderQueryService.java", r'''package com.example.minicommerce.order.application;

import static com.example.minicommerce.order.api.OrderDtos.OrderResponse;
import com.example.minicommerce.identity.domain.UserRole;
import com.example.minicommerce.order.infrastructure.OrderEntity;
import com.example.minicommerce.order.infrastructure.OrderItemRepository;
import com.example.minicommerce.order.infrastructure.OrderRepository;
import com.example.minicommerce.shared.error.BusinessException;
import com.example.minicommerce.shared.error.ErrorCode;
import com.example.minicommerce.shared.security.UserPrincipal;
import java.util.UUID;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

/**
 * 查询权限与写权限分离。SUPPORT 可在职责范围内读订单，但不能代替客户取消、支付或退款。
 * 对应文档：05_auth_security/02_RBAC与对象级权限.md。
 */
@Service
public class OrderQueryService {
    private final OrderRepository orders;
    private final OrderItemRepository items;

    public OrderQueryService(OrderRepository orders, OrderItemRepository items) {
        this.orders = orders;
        this.items = items;
    }

    @Transactional(readOnly = true)
    public OrderResponse get(UUID id, UserPrincipal actor) {
        OrderEntity order = orders.findById(id)
            .orElseThrow(() -> new BusinessException(ErrorCode.ORDER_NOT_FOUND, "订单不存在"));
        authorizeRead(order, actor);
        return view(order);
    }

    @Transactional(readOnly = true)
    public Page<OrderResponse> list(UserPrincipal actor, Pageable pageable) {
        Page<OrderEntity> page = actor.role() == UserRole.ADMIN || actor.role() == UserRole.SUPPORT
            ? orders.findAll(pageable)
            : orders.findByUserId(actor.id(), pageable);
        return page.map(this::view);
    }

    public OrderResponse view(OrderEntity order) {
        return OrderMapper.view(order, items.findByOrderIdOrderById(order.getId()));
    }

    public void authorizeRead(OrderEntity order, UserPrincipal actor) {
        if (!order.getUserId().equals(actor.id()) && actor.role() != UserRole.ADMIN && actor.role() != UserRole.SUPPORT) {
            throw new BusinessException(ErrorCode.ACCESS_DENIED, "不能访问他人的订单");
        }
    }

    public void authorizeOwner(OrderEntity order, UserPrincipal actor) {
        if (!order.getUserId().equals(actor.id())) {
            throw new BusinessException(ErrorCode.ACCESS_DENIED, "该操作只能由订单本人执行");
        }
    }

    public void authorizeOwnerOrAdmin(OrderEntity order, UserPrincipal actor) {
        if (!order.getUserId().equals(actor.id()) && actor.role() != UserRole.ADMIN) {
            throw new BusinessException(ErrorCode.ACCESS_DENIED, "该操作只能由订单本人或管理员执行");
        }
    }
}
''')

write("mini-commerce/backend/src/main/java/com/example/minicommerce/payment/infrastructure/PaymentAttemptRepository.java", r'''package com.example.minicommerce.payment.infrastructure;

import com.example.minicommerce.payment.domain.PaymentStatus;
import jakarta.persistence.LockModeType;
import java.time.Instant;
import java.util.Collection;
import java.util.Optional;
import java.util.UUID;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Lock;
import org.springframework.data.jpa.repository.Modifying;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

public interface PaymentAttemptRepository extends JpaRepository<PaymentAttemptEntity, UUID> {
    Optional<PaymentAttemptEntity> findByUserIdAndIdempotencyKey(Long userId, String idempotencyKey);

    boolean existsByOrderIdAndStatusIn(UUID orderId, Collection<PaymentStatus> statuses);

    @Lock(LockModeType.PESSIMISTIC_WRITE)
    @Query("select p from PaymentAttemptEntity p where p.id = :id")
    Optional<PaymentAttemptEntity> findForUpdate(@Param("id") UUID id);

    @Modifying(flushAutomatically = true, clearAutomatically = true)
    @Query(value = """
        update payment_attempts
           set status = 'PROCESSING', processing_started_at = now(), updated_at = now(), version = version + 1
         where id = :id
           and (status = 'INITIATED' or (status = 'PROCESSING' and processing_started_at < :stale))
        """, nativeQuery = true)
    int claim(@Param("id") UUID id, @Param("stale") Instant stale);
}
''')

write("mini-commerce/backend/src/main/java/com/example/minicommerce/order/application/OrderCommandService.java", r'''package com.example.minicommerce.order.application;

import static com.example.minicommerce.order.api.OrderDtos.OrderResponse;
import com.example.minicommerce.audit.application.AuditService;
import com.example.minicommerce.inventory.application.InventoryService;
import com.example.minicommerce.messaging.application.OutboxService;
import com.example.minicommerce.order.infrastructure.OrderEntity;
import com.example.minicommerce.order.infrastructure.OrderItemEntity;
import com.example.minicommerce.order.infrastructure.OrderItemRepository;
import com.example.minicommerce.order.infrastructure.OrderRepository;
import com.example.minicommerce.payment.domain.PaymentStatus;
import com.example.minicommerce.payment.infrastructure.PaymentAttemptRepository;
import com.example.minicommerce.promotion.application.CouponService;
import com.example.minicommerce.shared.error.BusinessException;
import com.example.minicommerce.shared.error.ErrorCode;
import com.example.minicommerce.shared.security.UserPrincipal;
import java.time.Clock;
import java.util.EnumSet;
import java.util.Map;
import java.util.UUID;
import java.util.stream.Collectors;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

/**
 * 取消订单与库存恢复、优惠券释放、Outbox 同事务。重复取消不会重复恢复库存。
 * 支付意图一旦处于 INITIATED/PROCESSING/UNKNOWN，取消必须拒绝，避免外部扣款成功后订单已被取消。
 */
@Service
public class OrderCommandService {
    private final OrderRepository orders;
    private final OrderItemRepository items;
    private final InventoryService inventory;
    private final CouponService coupons;
    private final PaymentAttemptRepository paymentAttempts;
    private final OutboxService outbox;
    private final OrderQueryService orderQuery;
    private final AuditService audit;
    private final Clock clock;

    public OrderCommandService(OrderRepository orders, OrderItemRepository items, InventoryService inventory,
                               CouponService coupons, PaymentAttemptRepository paymentAttempts, OutboxService outbox,
                               OrderQueryService orderQuery, AuditService audit, Clock clock) {
        this.orders = orders;
        this.items = items;
        this.inventory = inventory;
        this.coupons = coupons;
        this.paymentAttempts = paymentAttempts;
        this.outbox = outbox;
        this.orderQuery = orderQuery;
        this.audit = audit;
        this.clock = clock;
    }

    @Transactional
    public OrderResponse cancel(UUID id, UserPrincipal actor) {
        OrderEntity order = orders.findForUpdate(id)
            .orElseThrow(() -> new BusinessException(ErrorCode.ORDER_NOT_FOUND, "订单不存在"));
        orderQuery.authorizeOwnerOrAdmin(order, actor);
        var lines = items.findByOrderIdOrderById(id);
        if (order.getStatus().name().equals("CANCELLED")) return OrderMapper.view(order, lines);

        if (paymentAttempts.existsByOrderIdAndStatusIn(id,
            EnumSet.of(PaymentStatus.INITIATED, PaymentStatus.PROCESSING, PaymentStatus.UNKNOWN))) {
            throw new BusinessException(ErrorCode.ORDER_NOT_CANCELLABLE,
                "支付结果尚未确定，禁止取消；请先完成支付对账");
        }

        String before = order.getStatus().name();
        if (!order.cancel(clock.instant())) return OrderMapper.view(order, lines);
        Map<Long, Integer> quantities = lines.stream().collect(
            Collectors.toMap(OrderItemEntity::getProductId, OrderItemEntity::getQuantity));
        inventory.release(quantities);
        coupons.release(order.getUserCouponId(), id);
        outbox.append("ORDER", id.toString(), "order.cancelled.v1",
            Map.of("orderId", id, "userId", order.getUserId()));
        audit.record(actor.id(), "ORDER_CANCEL", "ORDER", id,
            Map.of("status", before), Map.of("status", order.getStatus()));
        return OrderMapper.view(order, lines);
    }
}
''')

write("mini-commerce/backend/src/main/java/com/example/minicommerce/payment/application/PaymentTransactionService.java", r'''package com.example.minicommerce.payment.application;

import com.example.minicommerce.audit.application.AuditService;
import com.example.minicommerce.inventory.application.InventoryService;
import com.example.minicommerce.messaging.application.OutboxService;
import com.example.minicommerce.order.application.IdempotencyLock;
import com.example.minicommerce.order.application.OrderQueryService;
import com.example.minicommerce.order.domain.OrderStatus;
import com.example.minicommerce.order.infrastructure.OrderEntity;
import com.example.minicommerce.order.infrastructure.OrderItemEntity;
import com.example.minicommerce.order.infrastructure.OrderItemRepository;
import com.example.minicommerce.order.infrastructure.OrderRepository;
import com.example.minicommerce.payment.domain.PaymentStatus;
import com.example.minicommerce.payment.infrastructure.PaymentAttemptEntity;
import com.example.minicommerce.payment.infrastructure.PaymentAttemptRepository;
import com.example.minicommerce.promotion.application.CouponService;
import com.example.minicommerce.shared.error.BusinessException;
import com.example.minicommerce.shared.error.ErrorCode;
import com.example.minicommerce.shared.security.UserPrincipal;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.time.Clock;
import java.util.HexFormat;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;
import java.util.stream.Collectors;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

/**
 * 支付 API 与订单 API 都持久化幂等语义。先读取幂等结果，再判断订单现态，
 * 因而第一次成功但响应丢失时，同 Key 重试仍返回原结果。
 */
@Service
public class PaymentTransactionService {
    private final PaymentAttemptRepository payments;
    private final OrderRepository orders;
    private final OrderItemRepository items;
    private final OrderQueryService orderQuery;
    private final InventoryService inventory;
    private final CouponService coupons;
    private final OutboxService outbox;
    private final AuditService audit;
    private final IdempotencyLock idempotencyLock;
    private final Clock clock;

    public PaymentTransactionService(PaymentAttemptRepository payments, OrderRepository orders,
                                     OrderItemRepository items, OrderQueryService orderQuery,
                                     InventoryService inventory, CouponService coupons, OutboxService outbox,
                                     AuditService audit, IdempotencyLock idempotencyLock, Clock clock) {
        this.payments = payments;
        this.orders = orders;
        this.items = items;
        this.orderQuery = orderQuery;
        this.inventory = inventory;
        this.coupons = coupons;
        this.outbox = outbox;
        this.audit = audit;
        this.idempotencyLock = idempotencyLock;
        this.clock = clock;
    }

    @Transactional
    public PaymentView createOrGet(UUID orderId, UserPrincipal actor, String key, String paymentToken) {
        if (key == null || key.isBlank()) {
            throw new BusinessException(ErrorCode.IDEMPOTENCY_KEY_REQUIRED, "支付必须提供 Idempotency-Key");
        }
        if (key.length() > 128) throw new BusinessException(ErrorCode.VALIDATION_ERROR, "Idempotency-Key 过长");
        idempotencyLock.acquire("payment:" + actor.id() + ":" + key);

        String requestHash = hash(orderId + ":" + paymentToken);
        Optional<PaymentAttemptEntity> prior = payments.findByUserIdAndIdempotencyKey(actor.id(), key);
        if (prior.isPresent()) {
            PaymentAttemptEntity payment = prior.get();
            if (!payment.getRequestHash().equals(requestHash) || !payment.getOrderId().equals(orderId)) {
                throw new BusinessException(ErrorCode.IDEMPOTENCY_CONFLICT, "同一支付幂等键不能用于不同请求");
            }
            return view(payment);
        }

        OrderEntity order = orders.findForUpdate(orderId)
            .orElseThrow(() -> new BusinessException(ErrorCode.ORDER_NOT_FOUND, "订单不存在"));
        orderQuery.authorizeOwner(order, actor);
        if (order.getStatus() != OrderStatus.PENDING_PAYMENT) {
            throw new BusinessException(ErrorCode.ORDER_NOT_PAYABLE, "订单不可支付");
        }
        PaymentAttemptEntity payment = payments.saveAndFlush(new PaymentAttemptEntity(
            UUID.randomUUID(), orderId, actor.id(), key, requestHash,
            order.getTotalAmount(), order.getCurrency(), clock.instant()));
        return view(payment);
    }

    @Transactional
    public boolean claim(UUID paymentId) {
        return payments.claim(paymentId, clock.instant().minusSeconds(120)) == 1;
    }

    @Transactional
    public PaymentView apply(UUID paymentId, PaymentGateway.GatewayResult result) {
        PaymentAttemptEntity payment = payments.findForUpdate(paymentId).orElseThrow();
        if (payment.getStatus() == PaymentStatus.SUCCEEDED || payment.getStatus() == PaymentStatus.DECLINED) {
            return view(payment);
        }

        if (result.success()) {
            OrderEntity order = orders.findForUpdate(payment.getOrderId()).orElseThrow();
            if (order.markPaid(payment.getId(), clock.instant())) {
                Map<Long, Integer> quantities = items.findByOrderIdOrderById(order.getId()).stream()
                    .collect(Collectors.toMap(OrderItemEntity::getProductId, OrderItemEntity::getQuantity));
                inventory.confirmSale(quantities);
                coupons.markUsed(order.getUserCouponId(), order.getId());
                outbox.append("ORDER", order.getId().toString(), "order.paid.v1", Map.of(
                    "orderId", order.getId(), "userId", order.getUserId(),
                    "total", order.getTotalAmount(), "currency", order.getCurrency()));
            }
            payment.succeeded(result.reference(), clock.instant());
            audit.record(payment.getUserId(), "PAYMENT_SUCCEEDED", "PAYMENT", payment.getId(), null,
                Map.of("orderId", payment.getOrderId(), "providerReference", result.reference()));
        } else if (result.unknown()) {
            payment.unknown(result.error(), clock.instant());
        } else {
            payment.declined(result.error(), clock.instant());
        }
        return view(payment);
    }

    @Transactional(readOnly = true)
    public PaymentView get(UUID id, UserPrincipal actor) {
        PaymentAttemptEntity payment = payments.findById(id).orElseThrow();
        if (!payment.getUserId().equals(actor.id()) && actor.role().name().equals("USER")) {
            throw new BusinessException(ErrorCode.ACCESS_DENIED, "不能读取他人的支付");
        }
        return view(payment);
    }

    private String hash(String value) {
        try {
            return HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256")
                .digest(value.getBytes(StandardCharsets.UTF_8)));
        } catch (Exception ex) {
            throw new IllegalStateException(ex);
        }
    }

    public static PaymentView view(PaymentAttemptEntity payment) {
        return new PaymentView(payment.getId(), payment.getOrderId(), payment.getStatus().name(),
            payment.getAmount(), payment.getCurrency(), payment.getProviderReference(), payment.getLastError());
    }

    public record PaymentView(UUID paymentId, UUID orderId, String status,
                              java.math.BigDecimal amount, String currency,
                              String providerReference, String error) {}
}
''')

write("mini-commerce/backend/src/main/java/com/example/minicommerce/notification/application/NotificationQueryService.java", r'''package com.example.minicommerce.notification.application;

import com.example.minicommerce.notification.infrastructure.NotificationEntity;
import com.example.minicommerce.notification.infrastructure.NotificationRepository;
import java.time.Instant;
import java.util.List;
import java.util.UUID;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class NotificationQueryService {
    private final NotificationRepository notifications;

    public NotificationQueryService(NotificationRepository notifications) {
        this.notifications = notifications;
    }

    @Transactional(readOnly = true)
    public List<View> list(Long userId) {
        return notifications.findTop50ByUserIdOrderByCreatedAtDesc(userId).stream()
            .map(NotificationQueryService::view)
            .toList();
    }

    private static View view(NotificationEntity notification) {
        return new View(notification.getId(), notification.getMessage(), notification.isUnread(),
            notification.getCreatedAt());
    }

    public record View(UUID id, String message, boolean unread, Instant createdAt) {}
}
''')

write("mini-commerce/backend/src/main/java/com/example/minicommerce/notification/api/NotificationController.java", r'''package com.example.minicommerce.notification.api;

import com.example.minicommerce.notification.application.NotificationQueryService;
import com.example.minicommerce.notification.application.NotificationQueryService.View;
import com.example.minicommerce.shared.security.CurrentUser;
import java.util.List;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

/** Controller 只调用 Application Service，架构规则由 ArchitectureTest 自动阻止层级穿透。 */
@RestController
@RequestMapping("/api/notifications")
public class NotificationController {
    private final NotificationQueryService service;
    private final CurrentUser currentUser;

    public NotificationController(NotificationQueryService service, CurrentUser currentUser) {
        this.service = service;
        this.currentUser = currentUser;
    }

    @GetMapping
    public List<View> list() {
        return service.list(currentUser.require().id());
    }
}
''')

# 退款增加 PROCESSING 与领取租约，防止相同请求并发调用外部退款两次。
write("mini-commerce/backend/src/main/java/com/example/minicommerce/refund/infrastructure/RefundEntity.java", r'''package com.example.minicommerce.refund.infrastructure;

import jakarta.persistence.*;
import java.math.BigDecimal;
import java.time.Instant;
import java.util.UUID;

@Entity
@Table(name = "refunds", uniqueConstraints = @UniqueConstraint(
    name = "ux_refund_payment_key", columnNames = {"payment_id", "idempotency_key"}))
public class RefundEntity {
    @Id private UUID id;
    @Column(name = "payment_id", nullable = false) private UUID paymentId;
    @Column(name = "order_id", nullable = false) private UUID orderId;
    @Column(name = "user_id", nullable = false) private Long userId;
    @Column(name = "idempotency_key", nullable = false, length = 128) private String key;
    @Column(nullable = false, length = 20) private String status;
    @Column(nullable = false, precision = 19, scale = 2) private BigDecimal amount;
    @Column(name = "provider_reference", length = 100) private String providerReference;
    @Column(name = "last_error", length = 500) private String lastError;
    @Column(name = "processing_started_at") private Instant processingStartedAt;
    @Column(name = "created_at", nullable = false) private Instant createdAt;
    @Column(name = "updated_at", nullable = false) private Instant updatedAt;
    @Version @Column(nullable = false) private long version;

    protected RefundEntity() {}

    public RefundEntity(UUID paymentId, UUID orderId, Long userId, String key, BigDecimal amount, Instant now) {
        this.id = UUID.randomUUID();
        this.paymentId = paymentId;
        this.orderId = orderId;
        this.userId = userId;
        this.key = key;
        this.amount = amount;
        this.status = "INITIATED";
        this.createdAt = now;
        this.updatedAt = now;
    }

    public UUID getId() { return id; }
    public UUID getPaymentId() { return paymentId; }
    public UUID getOrderId() { return orderId; }
    public Long getUserId() { return userId; }
    public String getStatus() { return status; }
    public BigDecimal getAmount() { return amount; }
    public String getProviderReference() { return providerReference; }
    public String getLastError() { return lastError; }
    public void success(String reference, Instant now) { status = "SUCCEEDED"; providerReference = reference; updatedAt = now; }
    public void unknown(String error, Instant now) { status = "UNKNOWN"; lastError = error; updatedAt = now; }
    public void failed(String error, Instant now) { status = "FAILED"; lastError = error; updatedAt = now; }
}
''')

write("mini-commerce/backend/src/main/java/com/example/minicommerce/refund/infrastructure/RefundRepository.java", r'''package com.example.minicommerce.refund.infrastructure;

import jakarta.persistence.LockModeType;
import java.time.Instant;
import java.util.Optional;
import java.util.UUID;
import org.springframework.data.jpa.repository.*;
import org.springframework.data.repository.query.Param;

public interface RefundRepository extends JpaRepository<RefundEntity, UUID> {
    Optional<RefundEntity> findByPaymentIdAndKey(UUID paymentId, String key);

    @Lock(LockModeType.PESSIMISTIC_WRITE)
    @Query("select r from RefundEntity r where r.id = :id")
    Optional<RefundEntity> findForUpdate(@Param("id") UUID id);

    @Modifying(flushAutomatically = true, clearAutomatically = true)
    @Query(value = """
        update refunds
           set status = 'PROCESSING', processing_started_at = now(), updated_at = now(), version = version + 1
         where id = :id
           and (status = 'INITIATED' or (status = 'PROCESSING' and processing_started_at < :stale))
        """, nativeQuery = true)
    int claim(@Param("id") UUID id, @Param("stale") Instant stale);
}
''')

write("mini-commerce/backend/src/main/java/com/example/minicommerce/refund/application/RefundTransactionService.java", r'''package com.example.minicommerce.refund.application;

import com.example.minicommerce.messaging.application.OutboxService;
import com.example.minicommerce.order.application.IdempotencyLock;
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

@Service
public class RefundTransactionService {
    private final RefundRepository refunds;
    private final PaymentAttemptRepository payments;
    private final OrderRepository orders;
    private final OrderQueryService orderQuery;
    private final OutboxService outbox;
    private final IdempotencyLock idempotencyLock;
    private final Clock clock;

    public RefundTransactionService(RefundRepository refunds, PaymentAttemptRepository payments,
                                    OrderRepository orders, OrderQueryService orderQuery,
                                    OutboxService outbox, IdempotencyLock idempotencyLock, Clock clock) {
        this.refunds = refunds;
        this.payments = payments;
        this.orders = orders;
        this.orderQuery = orderQuery;
        this.outbox = outbox;
        this.idempotencyLock = idempotencyLock;
        this.clock = clock;
    }

    @Transactional
    public RefundView begin(UUID paymentId, UserPrincipal actor, String key) {
        if (key == null || key.isBlank()) {
            throw new BusinessException(ErrorCode.IDEMPOTENCY_KEY_REQUIRED, "退款必须提供 Idempotency-Key");
        }
        idempotencyLock.acquire("refund:" + actor.id() + ":" + paymentId + ":" + key);
        Optional<RefundEntity> prior = refunds.findByPaymentIdAndKey(paymentId, key);
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
        orderQuery.authorizeOwnerOrAdmin(order, actor);
        order.requestRefund(clock.instant());
        return view(refunds.save(new RefundEntity(paymentId, order.getId(), actor.id(), key,
            payment.getAmount(), clock.instant())));
    }

    @Transactional
    public boolean claim(UUID refundId) {
        return refunds.claim(refundId, clock.instant().minusSeconds(120)) == 1;
    }

    @Transactional(readOnly = true)
    public RefundView get(UUID refundId) {
        return view(refunds.findById(refundId).orElseThrow());
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

/** 短事务登记意图 → 领取执行权 → 事务外调用支付机构 → 短事务落结果。 */
@Service
public class RefundOrchestrator {
    private final RefundTransactionService transactions;
    private final PaymentGateway gateway;

    public RefundOrchestrator(RefundTransactionService transactions, PaymentGateway gateway) {
        this.transactions = transactions;
        this.gateway = gateway;
    }

    public RefundView refund(UUID paymentId, UserPrincipal actor, String key) {
        RefundView intent = transactions.begin(paymentId, actor, key);
        if (!"INITIATED".equals(intent.status()) && !"PROCESSING".equals(intent.status())) return intent;
        if (!transactions.claim(intent.refundId())) return transactions.get(intent.refundId());
        PaymentGateway.GatewayResult result = gateway.refund(intent.refundId(), intent.amount());
        return transactions.finish(intent.refundId(), result);
    }
}
''')

write("mini-commerce/backend/src/main/resources/db/migration/V003__refunds.sql", r'''create table refunds(
 id uuid primary key,
 payment_id uuid not null references payment_attempts(id),
 order_id uuid not null references orders(id),
 user_id bigint not null references app_users(id),
 idempotency_key varchar(128) not null,
 status varchar(20) not null check(status in('INITIATED','PROCESSING','SUCCEEDED','FAILED','UNKNOWN')),
 amount numeric(19,2) not null check(amount>0),
 provider_reference varchar(100),
 last_error varchar(500),
 processing_started_at timestamptz,
 created_at timestamptz not null,
 updated_at timestamptz not null,
 version bigint not null default 0,
 constraint ux_refund_payment_key unique(payment_id,idempotency_key));
create index ix_refunds_order_created on refunds(order_id,created_at desc);
''')

# Publisher Return 与 Confirm 必须同时检查；未路由消息不能标记为 PUBLISHED。
outbox = PROJECT / "backend/src/main/java/com/example/minicommerce/messaging/application/OutboxPublisher.java"
outbox_text = outbox.read_text(encoding="utf-8")
outbox_text = outbox_text.replace(
    'mp.setContentEncoding(StandardCharsets.UTF_8.name());mp.setMessageId',
    'mp.setContentEncoding(StandardCharsets.UTF_8.name());mp.setDeliveryMode(MessageDeliveryMode.PERSISTENT);mp.setMessageId')
outbox_text = outbox_text.replace(
    'if(!confirm.isAck())throw new IllegalStateException("broker nack: "+confirm.getReason());repository.published',
    'if(!confirm.isAck())throw new IllegalStateException("broker nack: "+confirm.getReason());if(correlation.getReturned()!=null)throw new IllegalStateException("message unroutable: "+correlation.getReturned().getReplyText());repository.published')
outbox.write_text(outbox_text, encoding="utf-8")

# MCP Explain 只接受 SELECT/WITH，工具自行添加 EXPLAIN，避免 EXPLAIN EXPLAIN。
security = PROJECT / "mcp-server/src/mini_commerce_mcp/security.py"
security_text = security.read_text(encoding="utf-8")
security_text = security_text.replace(
    'if not (lower.startswith("select ") or lower.startswith("with ") or lower.startswith("explain ")):',
    'if not (lower.startswith("select ") or lower.startswith("with ")):')
security.write_text(security_text, encoding="utf-8")

# Health/SLO 基线：Readiness 包含数据库，HTTP Histogram 支持可聚合 P95/P99。
app_yml = PROJECT / "backend/src/main/resources/application.yml"
app_text = app_yml.read_text(encoding="utf-8")
app_text = app_text.replace(
    '      show-details: when_authorized\n  tracing:',
    '      show-details: when_authorized\n      group:\n        readiness:\n          include: readinessState,commerceDatabase\n  metrics:\n    distribution:\n      percentiles-histogram:\n        http.server.requests: true\n  tracing:')
app_yml.write_text(app_text, encoding="utf-8")

# 原文档 MANIFEST 已由 backup 分支保存；当前分支生成“文档 + 工程”的联合清单，避免旧哈希误导。
for cache in PROJECT.rglob("__pycache__"):
    if cache.is_dir(): shutil.rmtree(cache)

all_files = []
for path in REPO.rglob("*"):
    if not path.is_file() or ".git" in path.parts or path.name == "MANIFEST.md":
        continue
    if any(part in {"target", ".pytest_cache", "__pycache__"} for part in path.parts):
        continue
    all_files.append(path)

digest = hashlib.sha256()
for path in sorted(all_files):
    relative = path.relative_to(REPO).as_posix()
    digest.update(relative.encode("utf-8"))
    digest.update(b"\0")
    digest.update(hashlib.sha256(path.read_bytes()).digest())

counts = {
    "files": len(all_files),
    "markdown": sum(path.suffix.lower() == ".md" for path in all_files),
    "java": sum(path.suffix.lower() == ".java" for path in all_files),
    "sql": sum(path.suffix.lower() == ".sql" for path in all_files),
    "python": sum(path.suffix.lower() == ".py" for path in all_files),
    "yaml": sum(path.suffix.lower() in {".yml", ".yaml"} for path in all_files),
}
write("MANIFEST.md", f'''# 文档集群与完整工程联合清单

> 原始纯文档清单保存在分支 `backup/docs-only-2026-09-03`。
> 当前清单由发布脚本在生成完整工程后重新计算；不包含 `.git`、构建产物和本文件自身。

- 生成时间：{datetime.now(timezone.utc).isoformat()}
- 总文件数：{counts['files']}
- Markdown：{counts['markdown']}
- Java：{counts['java']}
- SQL：{counts['sql']}
- Python：{counts['python']}
- YAML：{counts['yaml']}
- 路径及内容聚合 SHA-256：`{digest.hexdigest()}`

## 主要组成

- `00_start`～`16_references`：完整学习文档集群；
- `FULL_BOOK.md`：文档合并阅读版；
- `mini-commerce/`：完整模块化单体工程、测试、Redis、RabbitMQ、可观测性、AWS、MCP 与 Eval；
- `mini-commerce/docs/generated/document-code-map.md`：文档章节到工程文件的逐项映射；
- `.github/workflows/`：生成、验证和发布门禁。

详细单文件哈希见 `mini-commerce/DELIVERY-MANIFEST.json`；原始文档快照与原哈希可在备份分支核对。
''')

print(json.dumps({"status": "release-fixes-applied", "counts": counts, "aggregateSha256": digest.hexdigest()}, ensure_ascii=False))
