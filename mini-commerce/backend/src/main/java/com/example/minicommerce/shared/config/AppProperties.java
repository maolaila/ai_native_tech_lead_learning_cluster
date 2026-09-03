package com.example.minicommerce.shared.config;

import java.time.Duration;
import org.springframework.boot.context.properties.ConfigurationProperties;

/**
 * 把 {@code application.yml} 和环境变量中的 {@code app.*} 配置集中装进一个有类型的 Java 对象。
 *
 * <p><strong>作用：</strong>统一管理 JWT、支付、缓存和 Outbox 配置。业务类只依赖这个对象，不需要在很多字段上重复写字符串形式的配置路径。
 *
 * <p><strong>大白话：</strong>配置文件像一张表，本类像一个整理好的配置盒子。Spring 启动时会按照名称把值放进对应位置。
 *
 * <p>例如：
 *
 * <pre>{@code
 * app:
 *   payment:
 *     read-timeout: 5s
 * }</pre>
 *
 * 会绑定到 {@code properties.payment().readTimeout()}。
 *
 * <p><strong>为什么不在业务类里到处写 {@code @Value}：</strong>{@code @Value("${...}")} 适合读取少量独立配置；
 * 本项目的配置是成组出现的。集中绑定更容易查看、改名、校验和测试，也不容易漏掉某个字符串路径。
 *
 * <p><strong>对应文档：</strong> {@code 02_backend_spring/05_日志_配置与健康检查.md}、 {@code
 * 08_runtime_deployment/03_配置_Secret与环境.md}、 {@code mini-commerce/docs/CONFIGURATION-FROM-ZERO.md}。
 */
// prefix = "app" 表示只读取 app.jwt、app.payment、app.cache、app.outbox 等配置。
@ConfigurationProperties(prefix = "app")
public record AppProperties(Jwt jwt, Payment payment, Cache cache, Outbox outbox) {

    /**
     * JWT 配置。
     *
     * @param issuer 谁签发了 Token
     * @param secret 用来签名和验证 Token 的密钥；生产环境不能使用公开默认值
     * @param accessTtl Access Token 有效期
     * @param refreshTtl Refresh Token 有效期
     */
    public record Jwt(String issuer, String secret, Duration accessTtl, Duration refreshTtl) {}

    /**
     * 支付相关配置。
     *
     * @param webhookSecret 验证支付回调签名的密钥
     * @param connectTimeout 最多等多久建立网络连接
     * @param readTimeout 连接建立后最多等多久收到响应
     */
    public record Payment(String webhookSecret, Duration connectTimeout, Duration readTimeout) {}

    /**
     * 商品缓存配置。
     *
     * @param productTtl 正常商品缓存多久
     * @param nullTtl “商品不存在”这个结果短暂缓存多久，用来降低缓存穿透
     * @param ttlJitter 给过期时间增加的随机范围，避免大量 Key 同时失效
     */
    public record Cache(Duration productTtl, Duration nullTtl, Duration ttlJitter) {}

    /**
     * Outbox 发布配置。
     *
     * @param batchSize 一次最多领取多少条待发布事件
     * @param lease 事件被某个发布器领取后，多久内归它处理
     * @param publishTimeout 等待 RabbitMQ Publisher Confirm 的最长时间
     * @param pollDelay 一轮扫描结束后等待多久再扫描
     */
    public record Outbox(
            int batchSize, Duration lease, Duration publishTimeout, Duration pollDelay) {}
}
