package com.example.minicommerce.shared.redis;

import java.time.Duration;
import java.util.Collections;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.data.redis.core.script.DefaultRedisScript;
import org.springframework.stereotype.Service;

/**
 * Lua 将 INCR 与首次设置过期时间作为一个原子操作，避免并发下窗口永不过期。 Redis 故障策略由调用方区分：登录可保守拒绝，普通读接口可受控 Fail Open。
 *
 * <p><strong>对应文档：</strong> {@code 02_backend_spring/01_请求生命周期与IoC_DI.md}、 {@code
 * 02_backend_spring/04_API设计_校验_异常与错误码.md}、 {@code 11_system_design/02_模块化单体与边界.md}。
 */
@Service
public class RateLimitService {
    private static final Logger log = LoggerFactory.getLogger(RateLimitService.class);
    private static final DefaultRedisScript<Long> FIXED_WINDOW =
            new DefaultRedisScript<>(
                    "local n=redis.call('incr',KEYS[1]); if n==1 then redis.call('pexpire',KEYS[1],ARGV[1]) end; return n",
                    Long.class);
    private final StringRedisTemplate redis;

    public RateLimitService(StringRedisTemplate redis) {
        this.redis = redis;
    }

    public boolean allow(String key, int limit, Duration window, boolean failOpen) {
        try {
            Long count =
                    redis.execute(
                            FIXED_WINDOW,
                            Collections.singletonList(key),
                            String.valueOf(window.toMillis()));
            return count != null && count <= limit;
        } catch (RuntimeException ex) {
            log.warn(
                    "event=redis_rate_limit_unavailable key={} failOpen={} reason={}",
                    key,
                    failOpen,
                    ex.getClass().getSimpleName());
            return failOpen;
        }
    }
}
