package com.example.minicommerce.cart.infrastructure;
import java.util.*; import org.springframework.data.jpa.repository.JpaRepository;
public interface CartItemRepository extends JpaRepository<CartItemEntity,Long>{List<CartItemEntity> findByCartIdOrderById(Long cartId);Optional<CartItemEntity> findByCartIdAndProductId(Long cartId,Long productId);void deleteByCartId(Long cartId);}
