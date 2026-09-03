package com.example.minicommerce.order.application;

import static com.example.minicommerce.order.api.OrderDtos.CreateOrderRequest;
import static com.example.minicommerce.order.api.OrderDtos.OrderLineRequest;
import static com.example.minicommerce.order.api.OrderDtos.OrderResponse;

import com.example.minicommerce.audit.application.AuditService;
import com.example.minicommerce.catalog.application.ProductService;
import com.example.minicommerce.catalog.infrastructure.ProductEntity;
import com.example.minicommerce.inventory.application.InventoryService;
import com.example.minicommerce.messaging.application.OutboxService;
import com.example.minicommerce.order.infrastructure.IdempotencyRecordEntity;
import com.example.minicommerce.order.infrastructure.IdempotencyRecordRepository;
import com.example.minicommerce.order.infrastructure.OrderEntity;
import com.example.minicommerce.order.infrastructure.OrderItemEntity;
import com.example.minicommerce.order.infrastructure.OrderItemRepository;
import com.example.minicommerce.order.infrastructure.OrderRepository;
import com.example.minicommerce.promotion.application.CouponService;
import com.example.minicommerce.shared.error.BusinessException;
import com.example.minicommerce.shared.error.ErrorCode;
import io.micrometer.core.instrument.MeterRegistry;
import java.math.BigDecimal;
import java.math.RoundingMode;
import java.time.Clock;
import java.time.ZoneOffset;
import java.time.format.DateTimeFormatter;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import java.util.SortedMap;
import java.util.TreeMap;
import java.util.TreeSet;
import java.util.UUID;
import org.slf4j.MDC;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

/**
 * 创建订单的主业务流程。
 *
 * <p><strong>作用：</strong>把幂等、商品校验、服务端计价、优惠券占用、库存预留、订单快照、Outbox 和审计按正确顺序组合起来。
 *
 * <p><strong>大白话：</strong>这个类像“下单总负责人”。它自己不直接写所有 SQL，而是调用各模块完成自己的部分，并保证关键数据库修改同成同败。
 *
 * <p><strong>对应文档：</strong> {@code 02_backend_spring/06_订单模块案例.md}、 {@code
 * 04_database_postgresql/04_事务与Spring边界.md}、 {@code 04_database_postgresql/05_并发_锁与库存超卖.md}、 {@code
 * 07_rabbitmq/04_幂等与Outbox.md}、 {@code mini-commerce/docs/REQUEST-TO-DATABASE-WALKTHROUGH.md}。
 */
// @Service：告诉 Spring，这个类主要负责一个业务用例，并由 Spring 创建和注入依赖。
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
            ProductService products,
            InventoryService inventory,
            CouponService coupons,
            OrderRepository orders,
            OrderItemRepository items,
            IdempotencyRecordRepository idempotency,
            IdempotencyLock lock,
            RequestFingerprint fingerprints,
            OutboxService outbox,
            OrderQueryService query,
            AuditService audit,
            Clock clock,
            MeterRegistry metrics) {
        this.products = products;
        this.inventory = inventory;
        this.coupons = coupons;
        this.orders = orders;
        this.items = items;
        this.idempotency = idempotency;
        this.lock = lock;
        this.fingerprints = fingerprints;
        this.outbox = outbox;
        this.query = query;
        this.audit = audit;
        this.clock = clock;
        this.metrics = metrics;
    }

    /**
     * 创建订单。
     *
     * <p><strong>{@code @Transactional} 的作用：</strong>从幂等记录到 Outbox 的数据库修改必须一起提交或一起回滚。
     * 外部支付不在本方法调用，因为慢网络请求不应该长时间占住数据库连接和锁。
     *
     * <p><strong>重要提醒：</strong>事务本身不会自动防止库存超卖。库存模块还需要数据库条件 UPDATE；幂等还需要锁、请求指纹和唯一约束。
     */
    @Transactional
    public OrderResponse create(Long userId, String idempotencyKey, CreateOrderRequest request) {

        // 第 1 步：幂等键是写请求的业务编号。网络超时后客户端重试时，系统据此复用原结果。
        if (idempotencyKey == null || idempotencyKey.isBlank()) {
            throw new BusinessException(
                    ErrorCode.IDEMPOTENCY_KEY_REQUIRED, "创建订单必须提供 Idempotency-Key");
        }
        if (idempotencyKey.length() > 128) {
            throw new BusinessException(ErrorCode.VALIDATION_ERROR, "Idempotency-Key 过长");
        }

        // 第 2 步：合并重复商品，并用 TreeMap 固定商品处理顺序，降低多商品并发时的死锁概率。
        SortedMap<Long, Integer> quantities = normalize(request);

        // 第 3 步：根据请求关键内容计算指纹。相同 Key 不能代表两种不同请求。
        String requestHash = fingerprints.order(quantities, request.couponCode());

        // 第 4 步：同一用户、同一幂等键的并发请求先串行处理，避免同时创建两张订单。
        lock.acquire(userId + ":" + idempotencyKey);

        // 第 5 步：如果以前已经处理过这个 Key，校验请求是否相同，并尽量直接返回原订单。
        Optional<IdempotencyRecordEntity> prior =
                idempotency.findByUserIdAndKey(userId, idempotencyKey);
        if (prior.isPresent()) {
            IdempotencyRecordEntity record = prior.get();
            if (!record.getRequestHash().equals(requestHash)) {
                throw new BusinessException(ErrorCode.IDEMPOTENCY_CONFLICT, "同一幂等键不能用于不同请求");
            }
            if ("COMPLETED".equals(record.getStatus())) {
                return query.view(orders.findById(record.getResourceId()).orElseThrow());
            }
        }

        var now = clock.instant();

        // 第 6 步：先保存“正在处理”的幂等记录。数据库唯一约束仍是并发下的最后防线。
        IdempotencyRecordEntity idempotencyRecord =
                idempotency.save(
                        new IdempotencyRecordEntity(userId, idempotencyKey, requestHash, now));

        // 第 7 步：重新读取数据库中的可售商品。这里不能只相信商品展示缓存。
        Map<Long, ProductEntity> foundProducts =
                products.authoritativeSellable(quantities.keySet());
        if (foundProducts.size() != quantities.size()) {
            Set<Long> missingProductIds = new TreeSet<>(quantities.keySet());
            missingProductIds.removeAll(foundProducts.keySet());
            throw new BusinessException(
                    ErrorCode.PRODUCT_NOT_SELLABLE,
                    "商品不存在或不可售",
                    Map.of("productIds", missingProductIds));
        }

        // 第 8 步：一张订单只允许一种币种，避免金额相加时含义不明确。
        String currency = foundProducts.values().iterator().next().getCurrency();
        if (foundProducts.values().stream()
                .anyMatch(product -> !currency.equals(product.getCurrency()))) {
            throw new BusinessException(ErrorCode.VALIDATION_ERROR, "一个订单不能混用多币种");
        }

        // 第 9 步：后端根据数据库价格计算小计。前端不能提交最终成交价。
        BigDecimal subtotal =
                quantities.entrySet().stream()
                        .map(
                                entry ->
                                        foundProducts
                                                .get(entry.getKey())
                                                .getPrice()
                                                .multiply(BigDecimal.valueOf(entry.getValue())))
                        .reduce(BigDecimal.ZERO, BigDecimal::add)
                        .setScale(2, RoundingMode.HALF_UP);

        UUID orderId = UUID.randomUUID();

        // 第 10 步：校验并占用优惠券。失败会抛异常，整个下单事务一起回滚。
        var reservedCoupon = coupons.reserve(request.couponCode(), userId, subtotal, orderId);

        // 第 11 步：原子预留库存。任何一个商品库存不足，整个事务回滚。
        inventory.reserve(quantities);

        // 第 12 步：计算最终金额，并保证结果不小于 0。
        BigDecimal total =
                subtotal.subtract(reservedCoupon.discount())
                        .max(BigDecimal.ZERO)
                        .setScale(2, RoundingMode.HALF_UP);

        // 对外展示的订单号使用日期和 UUID 前缀；真正主键仍是完整 UUID。
        String orderNumber =
                "MC-"
                        + DateTimeFormatter.BASIC_ISO_DATE.withZone(ZoneOffset.UTC).format(now)
                        + "-"
                        + orderId.toString().substring(0, 8).toUpperCase();

        // 第 13 步：保存订单主记录。
        OrderEntity order =
                orders.save(
                        new OrderEntity(
                                orderId,
                                orderNumber,
                                userId,
                                subtotal,
                                reservedCoupon.discount(),
                                total,
                                currency,
                                reservedCoupon.userCouponId(),
                                now));

        // 第 14 步：保存商品名称、SKU 和成交单价快照。商品以后改名或改价也不影响历史订单。
        List<OrderItemEntity> savedItems =
                quantities.entrySet().stream()
                        .map(
                                entry -> {
                                    ProductEntity product = foundProducts.get(entry.getKey());
                                    return new OrderItemEntity(
                                            orderId,
                                            product.getId(),
                                            product.getName(),
                                            product.getSku(),
                                            product.getPrice(),
                                            entry.getValue());
                                })
                        .toList();
        items.saveAll(savedItems);

        // 第 15 步：把待发布事件写进 Outbox。它和订单在同一个数据库事务中提交。
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

        // 第 16 步：幂等记录保存最终订单 ID，后续相同请求可以返回同一结果。
        idempotencyRecord.complete(orderId);

        // 第 17 步：记录谁创建了订单，方便审计和排查。
        audit.record(
                userId,
                "ORDER_CREATE",
                "ORDER",
                orderId,
                null,
                Map.of("status", order.getStatus(), "total", total));

        metrics.counter("commerce.orders.created").increment();
        return OrderMapper.view(order, savedItems);
    }

    /**
     * 合并重复商品并校验数量。
     *
     * <p>例如同一商品出现数量 1 和数量 2，会合并为数量 3。TreeMap 还会按商品 ID 排序， 让并发订单以尽量一致的顺序触碰库存行，从而降低死锁概率。
     */
    private SortedMap<Long, Integer> normalize(CreateOrderRequest request) {
        if (request.items() == null || request.items().isEmpty()) {
            throw new BusinessException(ErrorCode.ORDER_EMPTY, "订单不能为空");
        }

        SortedMap<Long, Integer> result = new TreeMap<>();
        for (OrderLineRequest line : request.items()) {
            if (line == null || line.productId() == null || line.quantity() <= 0) {
                throw new BusinessException(ErrorCode.VALIDATION_ERROR, "商品和数量非法");
            }
            result.merge(line.productId(), line.quantity(), Math::addExact);
        }
        return result;
    }
}
