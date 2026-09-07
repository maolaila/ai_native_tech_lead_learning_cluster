package com.example.minicommerce.cart.application;

import com.example.minicommerce.cart.infrastructure.CartEntity;
import com.example.minicommerce.cart.infrastructure.CartItemEntity;
import com.example.minicommerce.cart.infrastructure.CartItemRepository;
import com.example.minicommerce.cart.infrastructure.CartRepository;
import com.example.minicommerce.catalog.application.ProductService;
import com.example.minicommerce.order.application.IdempotencyLock;
import com.example.minicommerce.shared.error.BusinessException;
import com.example.minicommerce.shared.error.ErrorCode;
import java.util.List;
import java.util.Set;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

/**
 * 管理当前用户的购物车明细；PUT 将商品设置为指定数量，不是每调用一次再累加。
 *
 * <p><strong>作用：</strong>查询、设置和删除购物车商品。购物车不预留库存，也不固定最终价格。
 *
 * <p><strong>为什么：</strong>同一用户的修改共用事务级数据库锁，首次创建购物车也受到保护。 只锁已有的购物车行不够，因为第一次加入时还没有行可锁；唯一约束继续作为最后防线。
 *
 * <p><strong>对应文档：</strong>{@code 00_start/02_长期项目_Mini_Commerce.md}、 {@code
 * 04_database_postgresql/05_并发_锁与库存超卖.md}。
 */
@Service
public class CartService {
    private final CartRepository carts;
    private final CartItemRepository items;
    private final ProductService products;
    private final IdempotencyLock locks;

    public CartService(
            CartRepository carts,
            CartItemRepository items,
            ProductService products,
            IdempotencyLock locks) {
        this.carts = carts;
        this.items = items;
        this.products = products;
        this.locks = locks;
    }

    /** 设置最终数量；两个并发的相同 PUT 也只保存一条明细和一份指定数量。 */
    @Transactional
    public CartView put(Long userId, Long productId, int quantity) {
        if (productId == null || productId <= 0 || quantity <= 0) {
            throw new BusinessException(ErrorCode.VALIDATION_ERROR, "商品和数量必须大于 0");
        }
        lockCart(userId);
        // 加入购物车也不能只凭旧展示缓存判断上架状态；但此时不会保证未来仍有库存。
        if (!products.authoritativeSellable(Set.of(productId)).containsKey(productId)) {
            throw new BusinessException(ErrorCode.PRODUCT_NOT_SELLABLE, "商品不存在或不可售");
        }
        CartEntity cart =
                carts.findByUserId(userId).orElseGet(() -> carts.save(new CartEntity(userId)));
        CartItemEntity item =
                items.findByCartIdAndProductId(cart.getId(), productId)
                        .orElseGet(() -> new CartItemEntity(cart.getId(), productId, quantity));
        item.changeQuantity(quantity);
        items.save(item);
        return view(cart);
    }

    /** 删除当前用户的一条明细；与设置和清空使用同一个锁范围。 */
    @Transactional
    public void remove(Long userId, Long productId) {
        lockCart(userId);
        CartEntity cart =
                carts.findByUserId(userId)
                        .orElseThrow(
                                () ->
                                        new BusinessException(
                                                ErrorCode.CART_ITEM_NOT_FOUND, "购物车为空"));
        CartItemEntity item =
                items.findByCartIdAndProductId(cart.getId(), productId)
                        .orElseThrow(
                                () ->
                                        new BusinessException(
                                                ErrorCode.CART_ITEM_NOT_FOUND, "购物车项不存在"));
        items.delete(item);
    }

    @Transactional(readOnly = true)
    public CartView get(Long userId) {
        return carts.findByUserId(userId).map(this::view).orElse(new CartView(null, List.of()));
    }

    /** 清空只删除明细，不删除购物车所属用户。 */
    @Transactional
    public void clear(Long userId) {
        lockCart(userId);
        carts.findByUserId(userId).ifPresent(cart -> items.deleteByCartId(cart.getId()));
    }

    private void lockCart(Long userId) {
        // 此助手使用 PostgreSQL 事务锁；事务结束自动释放，不是只对单个 JVM 有效的锁。
        locks.acquire("cart:" + userId);
    }

    private CartView view(CartEntity cart) {
        return new CartView(
                cart.getId(),
                items.findByCartIdOrderById(cart.getId()).stream()
                        .map(item -> new CartLine(item.getProductId(), item.getQuantity()))
                        .toList());
    }

    public record CartView(Long cartId, List<CartLine> items) {}

    public record CartLine(Long productId, int quantity) {}
}
