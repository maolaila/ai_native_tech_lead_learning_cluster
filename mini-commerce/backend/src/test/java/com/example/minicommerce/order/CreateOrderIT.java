package com.example.minicommerce.order;

import static org.assertj.core.api.Assertions.*;

import com.example.minicommerce.catalog.infrastructure.*;
import com.example.minicommerce.identity.domain.UserRole;
import com.example.minicommerce.identity.infrastructure.*;
import com.example.minicommerce.inventory.infrastructure.*;
import com.example.minicommerce.messaging.infrastructure.OutboxEventRepository;
import com.example.minicommerce.order.api.OrderDtos.*;
import com.example.minicommerce.order.application.CreateOrderService;
import com.example.minicommerce.order.infrastructure.*;
import com.example.minicommerce.shared.error.BusinessException;
import com.example.minicommerce.support.AbstractPostgresIT;
import java.math.BigDecimal;
import java.util.*;
import org.junit.jupiter.api.*;
import org.springframework.beans.factory.annotation.Autowired;

/**
 * 订单模块的自动化验证层：{@code CreateOrderIT}。
 *
 * <p><strong>作用：</strong>提供可重复的行为、数据、并发或故障证据，而不是只证明代码能够编译。
 *
 * <p><strong>为什么：</strong>历史规则和 Bug 只有进入自动化测试，才不会在后续重构或 AI 生成代码时悄悄回归。
 *
 * <p><strong>对应文档：</strong> {@code 02_backend_spring/06_订单模块案例.md}、 {@code
 * 04_database_postgresql/04_事务与Spring边界.md}、 {@code 07_rabbitmq/04_幂等与Outbox.md}。
 */
class CreateOrderIT extends AbstractPostgresIT {
    @Autowired UserRepository users;
    @Autowired ProductRepository products;
    @Autowired InventoryRepository inventory;
    @Autowired CreateOrderService service;
    @Autowired OrderRepository orders;
    @Autowired IdempotencyRecordRepository idempotency;
    @Autowired OutboxEventRepository outbox;
    Long userId;
    Long productId;

    @BeforeEach
    void data() {
        UserEntity u =
                users.save(
                        new UserEntity(
                                UUID.randomUUID() + "@example.com",
                                "buyer",
                                "hash",
                                UserRole.USER));
        ProductEntity p =
                new ProductEntity(
                        "SKU-" + UUID.randomUUID(),
                        "快照商品",
                        "test",
                        new BigDecimal("8000.00"),
                        "JPY");
        p.publish();
        p = products.saveAndFlush(p);
        inventory.saveAndFlush(new InventoryEntity(p.getId(), 2));
        userId = u.getId();
        productId = p.getId();
    }

    @Test
    void create_writesOrderInventoryIdempotencyAndOutbox() {
        var result =
                service.create(
                        userId,
                        "key-" + UUID.randomUUID(),
                        new CreateOrderRequest(List.of(new OrderLineRequest(productId, 2)), null));
        assertThat(result.totalAmount()).isEqualByComparingTo("16000.00");
        assertThat(result.items().getFirst().productName()).isEqualTo("快照商品");
        assertThat(inventory.findById(productId).orElseThrow().getReserved()).isEqualTo(2);
        assertThat(idempotency.count()).isPositive();
        assertThat(outbox.count()).isPositive();
    }

    @Test
    void insufficientStock_rollsBackEveryWrite() {
        long beforeOrders = orders.count(),
                beforeIdem = idempotency.count(),
                beforeOutbox = outbox.count();
        assertThatThrownBy(
                        () ->
                                service.create(
                                        userId,
                                        "key-" + UUID.randomUUID(),
                                        new CreateOrderRequest(
                                                List.of(new OrderLineRequest(productId, 3)), null)))
                .isInstanceOf(BusinessException.class);
        assertThat(orders.count()).isEqualTo(beforeOrders);
        assertThat(idempotency.count()).isEqualTo(beforeIdem);
        assertThat(outbox.count()).isEqualTo(beforeOutbox);
        assertThat(inventory.findById(productId).orElseThrow().getAvailable()).isEqualTo(2);
    }
}
