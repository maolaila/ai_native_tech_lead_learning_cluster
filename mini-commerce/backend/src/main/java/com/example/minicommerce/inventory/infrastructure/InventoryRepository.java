package com.example.minicommerce.inventory.infrastructure;

import java.util.Optional;
import org.springframework.data.jpa.repository.*;
import org.springframework.data.repository.query.Param;
import jakarta.persistence.LockModeType;

public interface InventoryRepository extends JpaRepository<InventoryEntity,Long>{
    @Modifying(flushAutomatically=true,clearAutomatically=true)
    @Query(value="update inventory set available=available-:qty,reserved=reserved+:qty,version=version+1,updated_at=now() where product_id=:id and available>=:qty",nativeQuery=true)
    int reserve(@Param("id")Long id,@Param("qty")int qty);

    @Modifying(flushAutomatically=true,clearAutomatically=true)
    @Query(value="update inventory set available=available+:qty,reserved=reserved-:qty,version=version+1,updated_at=now() where product_id=:id and reserved>=:qty",nativeQuery=true)
    int release(@Param("id")Long id,@Param("qty")int qty);

    @Modifying(flushAutomatically=true,clearAutomatically=true)
    @Query(value="update inventory set reserved=reserved-:qty,version=version+1,updated_at=now() where product_id=:id and reserved>=:qty",nativeQuery=true)
    int confirmSale(@Param("id")Long id,@Param("qty")int qty);

    @Lock(LockModeType.PESSIMISTIC_WRITE) @Query("select i from InventoryEntity i where i.productId=:id")
    Optional<InventoryEntity> findForUpdate(@Param("id")Long id);
}
