package com.example.minicommerce.inventory.infrastructure;

import jakarta.persistence.LockModeType;
import java.util.Optional;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Lock;
import org.springframework.data.jpa.repository.Modifying;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

/**
 * 库存模块访问 PostgreSQL 的 Repository。
 *
 * <p><strong>作用：</strong>提供库存查询、预留、释放和确认成交所需的数据库操作。
 *
 * <p><strong>为什么这里使用原生 SQL：</strong>库存并发正确性依赖“检查库存是否足够”和“扣减库存”在同一条 UPDATE 中完成。
 * 直接写 SQL 能清楚看到数据库最终执行的条件，也便于用受影响行数判断成功或失败。
 *
 * <p><strong>对应文档：</strong> {@code 04_database_postgresql/04_事务与Spring边界.md}、 {@code
 * 04_database_postgresql/05_并发_锁与库存超卖.md}、 {@code 04_database_postgresql/06_隔离_MVCC与死锁.md}、 {@code
 * mini-commerce/docs/SPRING-JAVA-ANNOTATIONS.md}。
 */
// JpaRepository<InventoryEntity, Long> 表示：管理 InventoryEntity，主键类型是 Long。
public interface InventoryRepository extends JpaRepository<InventoryEntity, Long> {

    /**
     * 原子预留库存。
     *
     * <p>只有 {@code available >= qty} 时 UPDATE 才会成功。返回 1 表示更新了一行；返回 0 表示商品不存在或可用库存不足。
     */
    // @Modifying：下面的 @Query 会修改数据，不是普通 SELECT。
    @Modifying(flushAutomatically = true, clearAutomatically = true)
    // @Query：明确写出数据库执行的 SQL。nativeQuery = true 表示这里是 PostgreSQL 原生 SQL。
    @Query(
            value =
                    "update inventory set available=available-:qty,reserved=reserved+:qty,version=version+1,updated_at=now() where product_id=:id and available>=:qty",
            nativeQuery = true)
    // @Param 把 Java 参数 id、qty 绑定到 SQL 中的 :id、:qty。
    int reserve(@Param("id") Long id, @Param("qty") int qty);

    /** 取消订单时，把已预留数量归还到可用库存；条件防止 reserved 被减成负数。 */
    @Modifying(flushAutomatically = true, clearAutomatically = true)
    @Query(
            value =
                    "update inventory set available=available+:qty,reserved=reserved-:qty,version=version+1,updated_at=now() where product_id=:id and reserved>=:qty",
            nativeQuery = true)
    int release(@Param("id") Long id, @Param("qty") int qty);

    /** 支付成功后确认成交。下单时 available 已经减少，所以这里仅减少 reserved。 */
    @Modifying(flushAutomatically = true, clearAutomatically = true)
    @Query(
            value =
                    "update inventory set reserved=reserved-:qty,version=version+1,updated_at=now() where product_id=:id and reserved>=:qty",
            nativeQuery = true)
    int confirmSale(@Param("id") Long id, @Param("qty") int qty);

    /**
     * 读取并锁住一条库存记录，适合管理员整体替换库存等必须串行修改的场景。
     *
     * <p>悲观写锁会让其他事务等待，因此事务范围应尽量短，不能在持锁期间调用慢外部接口。
     */
    // @Lock(PESSIMISTIC_WRITE)：查询时加数据库写锁，直到当前事务结束。
    @Lock(LockModeType.PESSIMISTIC_WRITE)
    // 这里写的是 JPQL，InventoryEntity 和 productId 是 Java 实体名及字段名。
    @Query("select i from InventoryEntity i where i.productId=:id")
    Optional<InventoryEntity> findForUpdate(@Param("id") Long id);
}
