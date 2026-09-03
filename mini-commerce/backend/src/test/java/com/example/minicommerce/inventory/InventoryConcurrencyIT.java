package com.example.minicommerce.inventory;

import static org.assertj.core.api.Assertions.*;

import com.example.minicommerce.catalog.infrastructure.*;
import com.example.minicommerce.inventory.infrastructure.*;
import com.example.minicommerce.support.AbstractPostgresIT;
import java.math.BigDecimal;
import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicInteger;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.transaction.support.TransactionTemplate;

/**
 * 库存模块的自动化验证层：{@code InventoryConcurrencyIT}。
 *
 * <p><strong>作用：</strong>提供可重复的行为、数据、并发或故障证据，而不是只证明代码能够编译。
 *
 * <p><strong>为什么：</strong>历史规则和 Bug 只有进入自动化测试，才不会在后续重构或 AI 生成代码时悄悄回归。
 *
 * <p><strong>对应文档：</strong> {@code 04_database_postgresql/04_事务与Spring边界.md}、 {@code
 * 04_database_postgresql/05_并发_锁与库存超卖.md}、 {@code 04_database_postgresql/06_隔离_MVCC与死锁.md}。
 */
class InventoryConcurrencyIT extends AbstractPostgresIT {
    @Autowired ProductRepository products;
    @Autowired InventoryRepository inventory;
    @Autowired TransactionTemplate transactions;

    @Test
    void stockOne_twentyConcurrentReservations_onlyOneSucceeds() throws Exception {
        ProductEntity p =
                new ProductEntity(
                        "CONC-" + UUID.randomUUID(), "并发商品", "test", new BigDecimal("1.00"), "JPY");
        p.publish();
        p = products.saveAndFlush(p);
        inventory.saveAndFlush(new InventoryEntity(p.getId(), 1));
        int workers = 20;
        ExecutorService pool = Executors.newFixedThreadPool(workers);
        CountDownLatch ready = new CountDownLatch(workers), start = new CountDownLatch(1);
        AtomicInteger success = new AtomicInteger();
        List<Future<?>> futures = new ArrayList<>();
        Long id = p.getId();
        for (int n = 0; n < workers; n++)
            futures.add(
                    pool.submit(
                            () -> {
                                ready.countDown();
                                start.await();
                                transactions.executeWithoutResult(
                                        s -> {
                                            if (inventory.reserve(id, 1) == 1)
                                                success.incrementAndGet();
                                        });
                                return null;
                            }));
        ready.await(5, TimeUnit.SECONDS);
        start.countDown();
        for (Future<?> f : futures) f.get(10, TimeUnit.SECONDS);
        pool.shutdownNow();
        InventoryEntity finalState = inventory.findById(id).orElseThrow();
        assertThat(success.get()).isEqualTo(1);
        assertThat(finalState.getAvailable()).isZero();
        assertThat(finalState.getReserved()).isEqualTo(1);
    }
}
