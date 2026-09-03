package com.example.minicommerce.order.application;

import static com.example.minicommerce.order.api.OrderDtos.*;

import com.example.minicommerce.audit.application.AuditService;
import com.example.minicommerce.catalog.application.ProductService;
import com.example.minicommerce.catalog.infrastructure.ProductEntity;
import com.example.minicommerce.inventory.application.InventoryService;
import com.example.minicommerce.messaging.application.OutboxService;
import com.example.minicommerce.order.infrastructure.*;
import com.example.minicommerce.promotion.application.CouponService;
import com.example.minicommerce.shared.error.*;
import io.micrometer.core.instrument.MeterRegistry;
import java.math.*;
import java.time.Clock;
import java.time.format.DateTimeFormatter;
import java.util.*;
import org.slf4j.MDC;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

/**
 * 创建订单的强一致事务边界：权威商品读取、服务端计价、库存预留、优惠券占用、订单快照、幂等和 Outbox 同时提交或同时回滚。
 * 对应文档：02_backend_spring/06_订单模块案例.md、04_database_postgresql/04_事务与Spring边界.md、07_rabbitmq/04_幂等与Outbox.md。
 */
@Service
public class CreateOrderService {
    private final ProductService products;
    private final InventoryService inventory;
    private final CouponService coupons;
    private final OrderRepository orders;
    private final OrderItemRepository items;
    private final IdempotencyRecordRepository idempotency;
    private final IdempotencyLock lock;
    private final RequestFingerprint fingerprints;
    private final OutboxService outbox;
    private final OrderQueryService query;
    private final AuditService audit;
    private final Clock clock;
    private final MeterRegistry metrics;

    public CreateOrderService(
            ProductService p,
            InventoryService i,
            CouponService c,
            OrderRepository o,
            OrderItemRepository oi,
            IdempotencyRecordRepository ir,
            IdempotencyLock l,
            RequestFingerprint f,
            OutboxService out,
            OrderQueryService q,
            AuditService a,
            Clock clock,
            MeterRegistry m) {
        products = p;
        inventory = i;
        coupons = c;
        orders = o;
        items = oi;
        idempotency = ir;
        lock = l;
        fingerprints = f;
        outbox = out;
        query = q;
        audit = a;
        this.clock = clock;
        metrics = m;
    }

    /**
     * 学习说明：创建订单事务边界。
     *
     * <p>商品权威读取、服务端计价、库存预留、优惠券占用、订单快照、幂等结果和 Outbox 必须同成同败，因此放在一个数据库事务中。外部支付不在这里调用，避免长事务和不可回滚副作用。
     *
     * <p>对应文档：{@code 02_backend_spring/06_订单模块案例.md}、 {@code
     * 04_database_postgresql/04_事务与Spring边界.md}、 {@code 07_rabbitmq/04_幂等与Outbox.md}。
     */
    @Transactional
    public OrderResponse create(Long userId, String key, CreateOrderRequest request) {
        if (key == null || key.isBlank())
            throw new BusinessException(
                    ErrorCode.IDEMPOTENCY_KEY_REQUIRED, "创建订单必须提供 Idempotency-Key");
        if (key.length() > 128)
            throw new BusinessException(ErrorCode.VALIDATION_ERROR, "Idempotency-Key 过长");
        SortedMap<Long, Integer> quantities = normalize(request);
        String hash = fingerprints.order(quantities, request.couponCode());
        lock.acquire(userId + ":" + key);
        Optional<IdempotencyRecordEntity> prior = idempotency.findByUserIdAndKey(userId, key);
        if (prior.isPresent()) {
            IdempotencyRecordEntity r = prior.get();
            if (!r.getRequestHash().equals(hash))
                throw new BusinessException(ErrorCode.IDEMPOTENCY_CONFLICT, "同一幂等键不能用于不同请求");
            if ("COMPLETED".equals(r.getStatus()))
                return query.view(orders.findById(r.getResourceId()).orElseThrow());
        }
        var now = clock.instant();
        IdempotencyRecordEntity record =
                idempotency.save(new IdempotencyRecordEntity(userId, key, hash, now));
        Map<Long, ProductEntity> found = products.authoritativeSellable(quantities.keySet());
        if (found.size() != quantities.size()) {
            Set<Long> missing = new TreeSet<>(quantities.keySet());
            missing.removeAll(found.keySet());
            throw new BusinessException(
                    ErrorCode.PRODUCT_NOT_SELLABLE, "商品不存在或不可售", Map.of("productIds", missing));
        }
        String currency = found.values().iterator().next().getCurrency();
        if (found.values().stream().anyMatch(p -> !currency.equals(p.getCurrency())))
            throw new BusinessException(ErrorCode.VALIDATION_ERROR, "一个订单不能混用多币种");
        BigDecimal subtotal =
                quantities.entrySet().stream()
                        .map(
                                e ->
                                        found.get(e.getKey())
                                                .getPrice()
                                                .multiply(BigDecimal.valueOf(e.getValue())))
                        .reduce(BigDecimal.ZERO, BigDecimal::add)
                        .setScale(2, RoundingMode.HALF_UP);
        UUID orderId = UUID.randomUUID();
        var coupon = coupons.reserve(request.couponCode(), userId, subtotal, orderId);
        inventory.reserve(quantities);
        BigDecimal total =
                subtotal.subtract(coupon.discount())
                        .max(BigDecimal.ZERO)
                        .setScale(2, RoundingMode.HALF_UP);
        String number =
                "MC-"
                        + DateTimeFormatter.BASIC_ISO_DATE
                                .withZone(java.time.ZoneOffset.UTC)
                                .format(now)
                        + "-"
                        + orderId.toString().substring(0, 8).toUpperCase();
        OrderEntity order =
                orders.save(
                        new OrderEntity(
                                orderId,
                                number,
                                userId,
                                subtotal,
                                coupon.discount(),
                                total,
                                currency,
                                coupon.userCouponId(),
                                now));
        List<OrderItemEntity> saved =
                quantities.entrySet().stream()
                        .map(
                                e -> {
                                    ProductEntity p = found.get(e.getKey());
                                    return new OrderItemEntity(
                                            orderId,
                                            p.getId(),
                                            p.getName(),
                                            p.getSku(),
                                            p.getPrice(),
                                            e.getValue());
                                })
                        .toList();
        items.saveAll(saved);
        outbox.append(
                "ORDER",
                orderId.toString(),
                "order.created.v1",
                Map.of(
                        "orderId",
                        orderId,
                        "userId",
                        userId,
                        "total",
                        total,
                        "currency",
                        currency,
                        "traceId",
                        String.valueOf(MDC.get("traceId"))));
        record.complete(orderId);
        audit.record(
                userId,
                "ORDER_CREATE",
                "ORDER",
                orderId,
                null,
                Map.of("status", order.getStatus(), "total", total));
        metrics.counter("commerce.orders.created").increment();
        return OrderMapper.view(order, saved);
    }

    /**
     * 学习说明：先规范化订单项。
     *
     * <p>重复商品合并后再计算和扣减，避免一张订单出现多条相同商品；TreeMap 固定商品处理顺序， 使多个并发订单以相同顺序触碰库存行，从而降低多商品死锁概率。
     */
    private SortedMap<Long, Integer> normalize(CreateOrderRequest r) {
        if (r.items() == null || r.items().isEmpty())
            throw new BusinessException(ErrorCode.ORDER_EMPTY, "订单不能为空");
        SortedMap<Long, Integer> result = new TreeMap<>();
        for (OrderLineRequest line : r.items()) {
            if (line == null || line.productId() == null || line.quantity() <= 0)
                throw new BusinessException(ErrorCode.VALIDATION_ERROR, "商品和数量非法");
            result.merge(line.productId(), line.quantity(), Math::addExact);
        }
        return result;
    }
}
