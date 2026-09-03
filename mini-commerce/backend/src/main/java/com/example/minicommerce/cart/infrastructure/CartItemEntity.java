package com.example.minicommerce.cart.infrastructure;

import com.example.minicommerce.shared.persistence.BaseEntity;
import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import jakarta.persistence.UniqueConstraint;

/**
 * 购物车明细的 JPA 持久化实体，对应数据库表 {@code cart_items}。
 *
 * <p><strong>作用：</strong>保存“某个购物车中的某个商品及其数量”这一持久化事实。这个类只负责 ORM 映射与本实体的最小数据约束，不负责商品计价、库存判断或订单创建。
 *
 * <p><strong>为什么把购物车和购物车项拆成两张表：</strong>一个购物车可以包含多个商品，这是典型的一对多关系； 使用关联表能够建立外键、唯一约束和索引，也比把商品 ID
 * 列表塞进一个字符串字段更容易查询和维护。
 *
 * <p><strong>为什么有 {@code ux_cart_product} 唯一约束：</strong>同一购物车中的同一商品只能有一条明细。
 * 用户再次加入同一商品时应修改数量，而不是插入第二条重复记录。最终约束放在数据库，才能抵御并发请求绕过应用层的“先查再插”。
 *
 * <p><strong>对应文档：</strong> {@code 02_backend_spring/03_DTO_Entity_Domain与映射.md}、 {@code
 * 04_database_postgresql/01_关系模型_SQL与表关系.md}、 {@code 04_database_postgresql/02_约束_范式与数据建模.md}。
 */
@Entity
@Table(
        name = "cart_items",
        uniqueConstraints =
                @UniqueConstraint(
                        name = "ux_cart_product",
                        columnNames = {"cart_id", "product_id"}))
public class CartItemEntity extends BaseEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "cart_id", nullable = false)
    private Long cartId;

    @Column(name = "product_id", nullable = false)
    private Long productId;

    @Column(nullable = false)
    private int quantity;

    /** JPA 通过反射还原实体时需要无参构造器，因此保留为 {@code protected}，避免业务代码创建字段不完整的对象。 */
    protected CartItemEntity() {}

    /** 创建一条合法的购物车明细；首次创建时也走统一的数量校验，避免构造器和修改方法出现两套规则。 */
    public CartItemEntity(Long cartId, Long productId, int quantity) {
        this.cartId = cartId;
        this.productId = productId;
        changeQuantity(quantity);
    }

    public Long getId() {
        return id;
    }

    public Long getCartId() {
        return cartId;
    }

    public Long getProductId() {
        return productId;
    }

    public int getQuantity() {
        return quantity;
    }

    /**
     * 修改购物车数量。
     *
     * <p><strong>为什么不公开 {@code setQuantity}：</strong>有业务含义的方法能够集中保护“不允许零件或负数数量”的不变量，
     * 也让调用者和代码审查者一眼看出这是一次业务状态变化，而不是任意字段赋值。
     *
     * @param quantity 新数量，必须大于 0
     * @throws IllegalArgumentException 当数量小于等于 0 时抛出
     */
    public void changeQuantity(int quantity) {
        if (quantity <= 0) {
            throw new IllegalArgumentException("购物车商品数量必须大于 0");
        }
        this.quantity = quantity;
    }
}
