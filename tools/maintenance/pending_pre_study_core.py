"""One-use, assertion-guarded repair for the isolated pre-study audit branch.
The audit workflow removes this file after materializing and committing the changes.
"""
from pathlib import Path
root = Path.cwd()
j = root / 'mini-commerce/backend/src/main/java/com/example/minicommerce'
def edit(name, old, new):
    p = j / name
    text = p.read_text(encoding='utf-8')
    assert old in text, (name, old)
    p.write_text(text.replace(old, new), encoding='utf-8')

edit('inventory/infrastructure/InventoryRepository.java', ', clearAutomatically = true', '')
edit('inventory/infrastructure/InventoryRepository.java','    // @Modifying：下面的 @Query 会修改数据，不是普通 SELECT。','''    // @Modifying：下面的 @Query 会修改数据，不是普通 SELECT。
    // 先 flush 保存已有修改，但不能 clear 整个持久化上下文：那会让订单、支付、幂等记录都脱离 JPA 管理。
    // 原生 SQL 不会同步已加载的 InventoryEntity；调用链不要在更新前加载并继续复用旧库存实体。''')
edit('inventory/application/InventoryService.java','import org.springframework.transaction.annotation.Transactional;','import org.springframework.transaction.annotation.Transactional;\nimport org.springframework.transaction.annotation.Propagation;')
for method in ('initialize','reserve','release','confirmSale'):
    edit('inventory/application/InventoryService.java',f'    public void {method}(',f'    // MANDATORY：必须加入调用方已经开启的业务事务，不能把库存单独提交。\n    @Transactional(propagation = Propagation.MANDATORY)\n    public void {method}(')
edit('order/application/CreateOrderService.java','if (request.items() == null || request.items().isEmpty())','if (request == null || request.items() == null || request.items().isEmpty())')
edit('order/application/CreateOrderService.java','line.productId() == null || line.quantity() <= 0','line.productId() == null || line.productId() <= 0 || line.quantity() <= 0')
edit('order/application/CreateOrderService.java','            result.merge(line.productId(), line.quantity(), Math::addExact);','''            try {
                result.merge(line.productId(), line.quantity(), Math::addExact);
            } catch (ArithmeticException overflow) {
                throw new BusinessException(ErrorCode.VALIDATION_ERROR, "同一商品的合计数量过大");
            }''')
edit('order/application/CreateOrderService.java','orderId.toString().substring(0, 8).toUpperCase()', 'orderId.toString().replace("-", "").substring(0, 24).toUpperCase(java.util.Locale.ROOT)')
edit('order/application/CreateOrderService.java','// 对外展示的订单号使用日期和 UUID 前缀；真正主键仍是完整 UUID。','// 对外订单号使用日期与 24 位十六进制 UUID 前缀；避免原 8 位前缀的较高碰撞概率。数据库仍有唯一约束。')
edit('shared/error/ErrorCode.java','    IDEMPOTENCY_CONFLICT(HttpStatus.CONFLICT),','''    IDEMPOTENCY_CONFLICT(HttpStatus.CONFLICT),
    DATA_CONFLICT(HttpStatus.CONFLICT),
    PAYMENT_IN_PROGRESS(HttpStatus.CONFLICT),
    DEPENDENCY_BUSY(HttpStatus.SERVICE_UNAVAILABLE),''')
edit('shared/error/GlobalExceptionHandler.java','ErrorCode.IDEMPOTENCY_CONFLICT.name()', 'ErrorCode.DATA_CONFLICT.name()')
edit('shared/error/GlobalExceptionHandler.java','    @ExceptionHandler(Exception.class)','''    @ExceptionHandler({org.springframework.http.converter.HttpMessageNotReadableException.class,
            org.springframework.web.bind.ServletRequestBindingException.class,
            org.springframework.web.method.annotation.MethodArgumentTypeMismatchException.class,
            org.springframework.web.method.annotation.HandlerMethodValidationException.class})
    ResponseEntity<ProblemDetail> handleMalformedRequest(Exception exception) {
        return ResponseEntity.badRequest().body(base(HttpStatus.BAD_REQUEST,
                "请求格式错误，请检查 JSON、必填请求头以及路径参数类型", ErrorCode.VALIDATION_ERROR.name()));
    }

    @ExceptionHandler(org.springframework.web.ErrorResponseException.class)
    ResponseEntity<ProblemDetail> handleHttpError(org.springframework.web.ErrorResponseException exception) {
        HttpStatus status = HttpStatus.valueOf(exception.getStatusCode().value());
        return ResponseEntity.status(status).body(base(status, status.getReasonPhrase(), "HTTP_" + status.value()));
    }

    @ExceptionHandler(org.springframework.web.HttpRequestMethodNotSupportedException.class)
    ResponseEntity<ProblemDetail> handleMethod(org.springframework.web.HttpRequestMethodNotSupportedException exception) {
        return ResponseEntity.status(HttpStatus.METHOD_NOT_ALLOWED).headers(exception.getHeaders())
                .body(base(HttpStatus.METHOD_NOT_ALLOWED, "此地址不支持该 HTTP 方法", "HTTP_405"));
    }

    @ExceptionHandler(org.springframework.web.HttpMediaTypeNotSupportedException.class)
    ResponseEntity<ProblemDetail> handleMedia(org.springframework.web.HttpMediaTypeNotSupportedException exception) {
        return ResponseEntity.status(HttpStatus.UNSUPPORTED_MEDIA_TYPE).headers(exception.getHeaders())
                .body(base(HttpStatus.UNSUPPORTED_MEDIA_TYPE, "不支持该 Content-Type", "HTTP_415"));
    }

    @ExceptionHandler(org.springframework.web.servlet.resource.NoResourceFoundException.class)
    ResponseEntity<ProblemDetail> handleMissingResource(Exception exception) {
        return ResponseEntity.status(HttpStatus.NOT_FOUND).body(base(HttpStatus.NOT_FOUND, "资源不存在", "HTTP_404"));
    }

    @ExceptionHandler(org.springframework.dao.OptimisticLockingFailureException.class)
    ResponseEntity<ProblemDetail> handleVersionConflict(Exception exception) {
        return ResponseEntity.status(HttpStatus.CONFLICT).body(base(HttpStatus.CONFLICT,
                "数据已被其他请求修改，请重新读取后确认操作", ErrorCode.DATA_CONFLICT.name()));
    }

    @ExceptionHandler(Exception.class)''')
edit('shared/error/GlobalExceptionHandler.java','        problem.setProperty("traceId", traceId());','        problem.setProperty("traceId", traceId());\n        problem.setProperty("requestId", MDC.get("requestId"));')
edit('payment/infrastructure/PaymentAttemptRepository.java','    Optional<PaymentAttemptEntity> findByUserIdAndIdempotencyKey(Long userId, String key);','''    Optional<PaymentAttemptEntity> findByUserIdAndIdempotencyKey(Long userId, String key);

    // 在订单行锁保护下查询；UNKNOWN 不是失败，不能另开一笔支付。
    boolean existsByOrderIdAndStatusNot(UUID orderId, com.example.minicommerce.payment.domain.PaymentStatus status);''')
edit('payment/application/PaymentTransactionService.java','    private final Clock clock;', '    private final Clock clock;\n    private final IdempotencyLock idempotencyLock;')
edit('payment/application/PaymentTransactionService.java','            Clock clock) {','            Clock clock, IdempotencyLock idempotencyLock) {')
edit('payment/application/PaymentTransactionService.java','        this.clock = clock;','        this.clock = clock;\n        this.idempotencyLock = idempotencyLock;')
edit('payment/application/PaymentTransactionService.java','        String hash = hash(orderId + ":" + paymentToken);','''        if (key.length() > 128 || paymentToken == null || paymentToken.isBlank()) {
            throw new BusinessException(ErrorCode.VALIDATION_ERROR, "支付参数非法，幂等键最长 128 字符");
        }
        // 同一用户的相同键先串行；数据库唯一约束是最后防线，不是正常重试流程。
        idempotencyLock.acquire("payment:" + actor.id() + ":" + key);
        String hash = hash(orderId + ":" + paymentToken);''')
edit('payment/application/PaymentTransactionService.java','        PaymentAttemptEntity p =\n                payments.saveAndFlush(','''        if (payments.existsByOrderIdAndStatusNot(orderId, PaymentStatus.DECLINED)) {
            throw new BusinessException(ErrorCode.PAYMENT_IN_PROGRESS,
                    "订单已有支付记录，请使用原幂等键查询或等待核对，不能用新键重复扣款");
        }
        PaymentAttemptEntity p =
                payments.saveAndFlush(''')
edit('payment/application/PaymentOrchestrator.java','''        PaymentGateway.GatewayResult result =
                gateway.charge(p.paymentId(), p.amount(), p.currency(), token);''','''        PaymentGateway.GatewayResult result;
        try {
            // 数据库事务已结束。提供方必须以 paymentId 去重；网络超时不证明未扣款。
            result = gateway.charge(p.paymentId(), p.amount(), p.currency(), token);
        } catch (RuntimeException transportFailure) {
            result = PaymentGateway.GatewayResult.unknown("支付调用结果未知，需要使用原支付编号核对");
        }''')
edit('order/application/OrderCommandService.java','    private final Clock clock;', '    private final Clock clock;\n    private final com.example.minicommerce.payment.infrastructure.PaymentAttemptRepository payments;')
edit('order/application/OrderCommandService.java','            Clock clock) {','            Clock clock, com.example.minicommerce.payment.infrastructure.PaymentAttemptRepository payments) {')
edit('order/application/OrderCommandService.java','        this.clock = clock;', '        this.clock = clock;\n        this.payments = payments;')
edit('order/application/OrderCommandService.java','        String before = order.getStatus().name();','''        // 与创建支付意图使用同一把订单行锁，防止取消释放库存与外部扣款同时发生。
        if (order.getStatus() == com.example.minicommerce.order.domain.OrderStatus.PENDING_PAYMENT
                && payments.existsByOrderIdAndStatusNot(id,
                    com.example.minicommerce.payment.domain.PaymentStatus.DECLINED)) {
            throw new BusinessException(ErrorCode.PAYMENT_IN_PROGRESS, "支付正在处理或结果未知，核对完成前不能取消");
        }
        String before = order.getStatus().name();''')
p=j/'refund/application/RefundService.java'
new=p.read_text(encoding='utf-8').replace('import com.example.minicommerce.shared.security.UserPrincipal;', 'import com.example.minicommerce.shared.security.UserPrincipal;\nimport com.example.minicommerce.refund.application.RefundService.RefundView;')
new=new.replace('public class RefundService {','public class RefundTransactionService {').replace('public RefundService(', 'public RefundTransactionService(')
new=new.replace('    private final PaymentGateway gateway;\n','').replace('            PaymentGateway g,\n','').replace('        gateway = g;\n','')
start=new.index('    public RefundView refund(')
end=new.index('    @Transactional',start)
new=new[:start]+new[end:]
new=new[:new.index('    public record RefundView(')]+'}\n'
new=new.replace('RefundService}', 'RefundTransactionService}')
new=new.replace('''        Optional<RefundEntity> prior = refunds.findByPaymentIdAndKey(paymentId, key);
        if (prior.isPresent()) return view(prior.get());''','''        if (key.length() > 128) {
            throw new BusinessException(ErrorCode.VALIDATION_ERROR, "退款幂等键最长 128 字符");
        }''')
needle='        if (payment.getStatus() != com.example.minicommerce.payment.domain.PaymentStatus.SUCCEEDED)'
new=new.replace(needle,'''        // 先授权再查重：幂等重放也不能泄露他人的退款结果。
        Optional<RefundEntity> prior = refunds.findByPaymentIdAndKey(paymentId, key);
        if (prior.isPresent()) return view(prior.get());
        if (refunds.existsByPaymentIdAndStatusNot(paymentId, "FAILED")) {
            throw new BusinessException(ErrorCode.ORDER_NOT_REFUNDABLE, "已有退款记录，请使用原键核对结果");
        }
'''+needle)
new=new.replace('    @Transactional\n    public RefundView finish', '''    /** 领取执行权；并发重试只有一个请求能把 INITIATED 改为 PROCESSING。 */
    @Transactional
    public boolean claim(UUID id) {
        RefundEntity refund = refunds.findForUpdate(id).orElseThrow();
        return refund.claim(clock.instant());
    }

    @Transactional(readOnly = true)
    public RefundView get(UUID id) {
        return view(refunds.findById(id).orElseThrow());
    }

    @Transactional
    public RefundView finish''')
(j/'refund/application/RefundTransactionService.java').write_text(new,encoding='utf-8')
p.write_text('''package com.example.minicommerce.refund.application;

import com.example.minicommerce.payment.application.PaymentGateway;
import com.example.minicommerce.shared.security.UserPrincipal;
import java.math.BigDecimal;
import java.util.UUID;
import org.springframework.stereotype.Service;

/**
 * 退款流程的三段式编排：短事务登记 → 事务外请求提供方 → 短事务保存结果。
 *
 * <p><strong>为什么拆成两个 Bean：</strong>同一个对象直接调用自己的 @Transactional 方法不会经过 Spring 代理。
 * 本类调用独立的 RefundTransactionService，让事务真正生效，而不是只在方法上贴注解。
 *
 * <p>本项目只演示付款后的全额退款，不连接真实资金系统；UNKNOWN 必须核对，不能假定失败后再退款。
 *
 * <p><strong>对应文档：</strong>{@code 04_database_postgresql/04_事务与Spring边界.md}、
 * {@code mini-commerce/docs/testing-strategy.md}。
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

    public record RefundView(UUID refundId, UUID paymentId, UUID orderId, String status,
            BigDecimal amount, String providerReference, String error) {}
}
''',encoding='utf-8')
edit('refund/infrastructure/RefundEntity.java','    public void success(String ref, Instant now) {','''    public boolean claim(Instant now) {
        if (!"INITIATED".equals(status)) return false;
        status = "PROCESSING";
        updatedAt = now;
        return true;
    }

    public void success(String ref, Instant now) {''')
edit('refund/infrastructure/RefundRepository.java','    Optional<RefundEntity> findByPaymentIdAndKey(UUID paymentId, String key);','''    Optional<RefundEntity> findByPaymentIdAndKey(UUID paymentId, String key);

    boolean existsByPaymentIdAndStatusNot(UUID paymentId, String status);''')
edit('payment/application/PaymentGateway.java','GatewayResult refund(UUID paymentId, BigDecimal amount);','GatewayResult refund(UUID refundId, UUID paymentId, BigDecimal amount);')
edit('payment/application/FakePaymentGateway.java','public GatewayResult refund(UUID id, BigDecimal amount)', 'public GatewayResult refund(UUID id, UUID paymentId, BigDecimal amount)')
edit('order/infrastructure/OrderEntity.java','''        if (status == OrderStatus.REFUNDING) return;
        if (status != OrderStatus.PAID && status != OrderStatus.FULFILLING)''','''        // 教学闭环只允许付款后、履约前全额退款；退货和履约补偿属于后续练习。
        if (status != OrderStatus.PAID)''')
(root/'mini-commerce/backend/src/test/resources/application.yml').unlink()
p=root/'mini-commerce/backend/src/main/resources/application-test.yml'
s=p.read_text(encoding='utf-8').replace('  task:\n    scheduling:\n      enabled: false\n','').replace('  outbox:\n','  outbox:\n    publisher-enabled: false\n')
p.write_text(s,encoding='utf-8')
for name in ('catalog/infrastructure/ProductEntity.java','order/infrastructure/OrderEntity.java','payment/infrastructure/PaymentAttemptEntity.java'):
    edit(name,'    private String currency;', '    @org.hibernate.annotations.JdbcTypeCode(org.hibernate.type.SqlTypes.CHAR)\n    private String currency;')
for name in ('payment/application/PaymentWebhookService.java','notification/application/OrderPaidConsumers.java','catalog/application/ProductCacheInvalidationConsumer.java'):
    edit(name,'    @Transactional\n', '    @Transactional(rollbackFor = Exception.class)\n')
(root/'mini-commerce/backend/src/main/resources/db/migration/V004__payment_refund_safety.sql').write_text('''-- 不修改 V001～V003：Flyway 用校验和保护已经执行过的迁移。
-- 结果未知也占用执行槽位；不能等实际重复扣款后才靠成功状态唯一约束补救。
-- 若旧演示数据已有多条未终结支付，本迁移会安全失败，需要先核对，不能随意改为失败。
create unique index ux_payment_one_active_order
    on payment_attempts(order_id) where status <> 'DECLINED';

alter table refunds drop constraint refunds_status_check;
alter table refunds add constraint refunds_status_check
    check (status in ('INITIATED', 'PROCESSING', 'SUCCEEDED', 'FAILED', 'UNKNOWN'));
create unique index ux_refund_one_active_payment
    on refunds(payment_id) where status <> 'FAILED';
''',encoding='utf-8')
print('Reviewed core repairs materialized; run regression tests before promotion.')
