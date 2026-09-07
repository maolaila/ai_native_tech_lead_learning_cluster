package com.example.minicommerce.order.application;

import com.fasterxml.jackson.databind.ObjectMapper;
import java.security.*;
import java.util.*;
import java.util.HexFormat;
import org.springframework.stereotype.Component;

/**
 * 把下单的关键内容转换成稳定的 SHA-256 请求指纹。
 *
 * <p><strong>作用：</strong>把下单的关键内容转换成稳定的 SHA-256 请求指纹。
 *
 * <p><strong>为什么：</strong>先合并和排序商品，再算指纹；仅改变商品输入顺序不应被误判为另一种业务请求。哈希不是对请求内容加密。
 *
 * <p><strong>对应文档：</strong> {@code 02_backend_spring/06_订单模块案例.md}、 {@code
 * 04_database_postgresql/04_事务与Spring边界.md}、 {@code 07_rabbitmq/04_幂等与Outbox.md}。
 */
@Component
public class RequestFingerprint {
    private final ObjectMapper json;

    public RequestFingerprint(ObjectMapper json) {
        this.json = json;
    }

    public String order(SortedMap<Long, Integer> items, String coupon) {
        try {
            byte[] data =
                    json.writeValueAsBytes(
                            Map.of(
                                    "items",
                                    items,
                                    "coupon",
                                    coupon == null ? "" : coupon.trim().toUpperCase()));
            return HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(data));
        } catch (Exception e) {
            throw new IllegalStateException(e);
        }
    }
}
