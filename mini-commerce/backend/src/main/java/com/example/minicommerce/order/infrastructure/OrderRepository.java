package com.example.minicommerce.order.infrastructure;
import java.util.*;import org.springframework.data.domain.*;import org.springframework.data.jpa.repository.*;import org.springframework.data.repository.query.Param;import jakarta.persistence.LockModeType;
public interface OrderRepository extends JpaRepository<OrderEntity,UUID>{@Lock(LockModeType.PESSIMISTIC_WRITE)@Query("select o from OrderEntity o where o.id=:id")Optional<OrderEntity> findForUpdate(@Param("id")UUID id);Page<OrderEntity> findByUserId(Long userId,Pageable pageable);}
