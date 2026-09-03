package com.example.minicommerce.inventory.application;

import com.example.minicommerce.inventory.infrastructure.*;
import com.example.minicommerce.shared.error.*;
import java.util.*;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

/**
 * 库存预留使用数据库条件 UPDATE。@Transactional 只保证事务原子性，并不能自动防止两个事务同时读到 stock=1。
 * 对应文档：04_database_postgresql/04_事务与Spring边界.md、04_database_postgresql/05_并发_锁与库存超卖.md。
 */
@Service
public class InventoryService {
    private final InventoryRepository repository;

    public InventoryService(InventoryRepository repository) {
        this.repository = repository;
    }

    public void initialize(Long productId, int stock) {
        repository.save(new InventoryEntity(productId, stock));
    }

    /**
     * 学习说明：库存预留不能使用“查询库存→Java 中减法→保存”的普通读改写。
     *
     * <p>Repository 使用带条件的原子 UPDATE；受影响行数为 0 就表示库存不足。 即使多个事务同时到达，数据库也只会让满足条件的更新成功。
     */
    public void reserve(Map<Long, Integer> quantities) {
        quantities.entrySet().stream()
                .sorted(Map.Entry.comparingByKey())
                .forEach(
                        e -> {
                            if (repository.reserve(e.getKey(), e.getValue()) != 1)
                                throw new BusinessException(
                                        ErrorCode.INSUFFICIENT_STOCK,
                                        "库存不足",
                                        Map.of("productId", e.getKey(), "quantity", e.getValue()));
                        });
    }

    /** 学习说明：取消订单时把 reserved 数量恢复为 available。 调用方必须先通过订单状态机保证取消只发生一次，并与订单状态修改处于同一事务。 */
    public void release(Map<Long, Integer> quantities) {
        quantities.entrySet().stream()
                .sorted(Map.Entry.comparingByKey())
                .forEach(
                        e -> {
                            if (repository.release(e.getKey(), e.getValue()) != 1)
                                throw new IllegalStateException(
                                        "预留库存数据不一致 productId=" + e.getKey());
                        });
    }

    /** 学习说明：支付成功后只减少 reserved，不再减少 available，因为下单时已经完成预留。 这样可以清楚区分“可售”“已预留”和“已成交”三个业务事实。 */
    public void confirmSale(Map<Long, Integer> quantities) {
        quantities.entrySet().stream()
                .sorted(Map.Entry.comparingByKey())
                .forEach(
                        e -> {
                            if (repository.confirmSale(e.getKey(), e.getValue()) != 1)
                                throw new IllegalStateException(
                                        "确认库存数据不一致 productId=" + e.getKey());
                        });
    }

    @Transactional
    public InventoryView replaceAvailable(Long productId, int available) {
        InventoryEntity i =
                repository
                        .findForUpdate(productId)
                        .orElseThrow(
                                () ->
                                        new BusinessException(
                                                ErrorCode.INVENTORY_NOT_FOUND, "库存不存在"));
        i.replaceAvailable(available);
        return view(i);
    }

    @Transactional(readOnly = true)
    public InventoryView get(Long productId) {
        return repository
                .findById(productId)
                .map(InventoryService::view)
                .orElseThrow(() -> new BusinessException(ErrorCode.INVENTORY_NOT_FOUND, "库存不存在"));
    }

    private static InventoryView view(InventoryEntity i) {
        return new InventoryView(
                i.getProductId(), i.getAvailable(), i.getReserved(), i.getVersion());
    }

    public record InventoryView(Long productId, int available, int reserved, long version) {}
}
