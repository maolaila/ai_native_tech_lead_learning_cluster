package com.example.minicommerce.cart.infrastructure;
import com.example.minicommerce.shared.persistence.BaseEntity; import jakarta.persistence.*;
@Entity @Table(name="carts",uniqueConstraints=@UniqueConstraint(name="ux_cart_user",columnNames="user_id"))
public class CartEntity extends BaseEntity{@Id @GeneratedValue(strategy=GenerationType.IDENTITY)private Long id;@Column(name="user_id",nullable=false)private Long userId;protected CartEntity(){}public CartEntity(Long userId){this.userId=userId;}public Long getId(){return id;}public Long getUserId(){return userId;}}
