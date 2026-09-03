package com.example.minicommerce.cart.application;

import com.example.minicommerce.cart.infrastructure.*;import com.example.minicommerce.catalog.application.ProductService;import com.example.minicommerce.shared.error.*;import java.util.*;import org.springframework.stereotype.Service;import org.springframework.transaction.annotation.Transactional;

@Service public class CartService{
 private final CartRepository carts;private final CartItemRepository items;private final ProductService products;
 public CartService(CartRepository c,CartItemRepository i,ProductService p){carts=c;items=i;products=p;}
 @Transactional public CartView put(Long userId,Long productId,int quantity){products.getPublic(productId);CartEntity c=carts.findByUserId(userId).orElseGet(()->carts.save(new CartEntity(userId)));CartItemEntity item=items.findByCartIdAndProductId(c.getId(),productId).orElseGet(()->new CartItemEntity(c.getId(),productId,quantity));item.changeQuantity(quantity);items.save(item);return view(c);}
 @Transactional public void remove(Long userId,Long productId){CartEntity c=carts.findByUserId(userId).orElseThrow(()->new BusinessException(ErrorCode.CART_ITEM_NOT_FOUND,"购物车为空"));CartItemEntity i=items.findByCartIdAndProductId(c.getId(),productId).orElseThrow(()->new BusinessException(ErrorCode.CART_ITEM_NOT_FOUND,"购物车项不存在"));items.delete(i);}
 @Transactional(readOnly=true) public CartView get(Long userId){return carts.findByUserId(userId).map(this::view).orElse(new CartView(null,List.of()));}
 @Transactional public void clear(Long userId){carts.findByUserId(userId).ifPresent(c->items.deleteByCartId(c.getId()));}
 private CartView view(CartEntity c){return new CartView(c.getId(),items.findByCartIdOrderById(c.getId()).stream().map(i->new CartLine(i.getProductId(),i.getQuantity())).toList());}
 public record CartView(Long cartId,List<CartLine> items){}public record CartLine(Long productId,int quantity){}
}
