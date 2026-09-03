package com.example.minicommerce.cart.infrastructure;
import java.util.Optional; import org.springframework.data.jpa.repository.JpaRepository;
public interface CartRepository extends JpaRepository<CartEntity,Long>{Optional<CartEntity> findByUserId(Long userId);}
