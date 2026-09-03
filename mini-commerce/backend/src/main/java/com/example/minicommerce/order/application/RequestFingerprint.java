package com.example.minicommerce.order.application;

import com.fasterxml.jackson.databind.ObjectMapper;
import java.security.*;
import java.util.*;
import java.util.HexFormat;
import org.springframework.stereotype.Component;

/**
 * 订单模块的应用用例编排层：{@code RequestFingerprint}。
 *
 * <p><strong>作用：</strong>编排一个完整业务用例，协调领域规则、仓储、外部端口与事务边界。
 *
 * <p><strong>为什么：</strong>事务应该围绕业务动作，而不是分散在 Controller 或每个 Repository 中。
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
