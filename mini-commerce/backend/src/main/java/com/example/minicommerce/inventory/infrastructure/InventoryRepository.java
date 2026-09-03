package com.example.minicommerce.inventory.infrastructure;

import jakarta.persistence.LockModeType;
import java.util.Optional;
import org.springframework.data.jpa.repository.*;
import org.springframework.data.repository.query.Param;

/**
 * 库存模块的基础设施适配层：{@code InventoryRepository}。
 *
 * <p><strong>作用：</strong>负责 JPA、SQL、Redis、RabbitMQ 或外部系统等技术实现，并把技术细节隔离在业务边界之外。
 *
 * <p><strong>为什么：</strong>数据库表和框架会变化；隔离适配器可以避免这些变化扩散到业务规则和 API 契约。
 *
 * <p><strong>对应文档：</strong> {@code 04_database_postgresql/04_事务与Spring边界.md}、 {@code
 * 04_database_postgresql/05_并发_锁与库存超卖.md}、 {@code 04_database_postgresql/06_隔离_MVCC与死锁.md}。
 */
public interface InventoryRepository extends JpaRepository<InventoryEntity, Long> {
    @Modifying(flushAutomatically = true, clearAutomatically = true)
    @Query(
            value =
                    "update inventory set available=available-:qty,reserved=reserved+:qty,version=version+1,updated_at=now() where product_id=:id and available>=:qty",
            nativeQuery = true)
    int reserve(@Param("id") Long id, @Param("qty") int qty);

    @Modifying(flushAutomatically = true, clearAutomatically = true)
    @Query(
            value =
                    "update inventory set available=available+:qty,reserved=reserved-:qty,version=version+1,updated_at=now() where product_id=:id and reserved>=:qty",
            nativeQuery = true)
    int release(@Param("id") Long id, @Param("qty") int qty);

    @Modifying(flushAutomatically = true, clearAutomatically = true)
    @Query(
            value =
                    "update inventory set reserved=reserved-:qty,version=version+1,updated_at=now() where product_id=:id and reserved>=:qty",
            nativeQuery = true)
    int confirmSale(@Param("id") Long id, @Param("qty") int qty);

    @Lock(LockModeType.PESSIMISTIC_WRITE)
    @Query("select i from InventoryEntity i where i.productId=:id")
    Optional<InventoryEntity> findForUpdate(@Param("id") Long id);
}
