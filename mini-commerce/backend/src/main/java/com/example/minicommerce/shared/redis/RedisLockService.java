package com.example.minicommerce.shared.redis;

import java.time.Duration;
import java.util.Collections;
import java.util.UUID;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.data.redis.core.script.DefaultRedisScript;
import org.springframework.stereotype.Service;

/**
 * 短期互斥锁仅用于缓存回源等可容错场景；库存正确性仍由 PostgreSQL 条件 UPDATE/行锁保证。
 * 对应文档：06_redis/04_限流_Session与分布式锁.md。
 */
@Service
public class RedisLockService {
    private static final DefaultRedisScript<Long> RELEASE = new DefaultRedisScript<>(
        "if redis.call('get', KEYS[1]) == ARGV[1] then return redis.call('del', KEYS[1]) else return 0 end", Long.class);
    private final StringRedisTemplate redis;
    public RedisLockService(StringRedisTemplate redis) { this.redis = redis; }

    public LockHandle tryLock(String key, Duration ttl) {
        String owner = UUID.randomUUID().toString();
        Boolean acquired = redis.opsForValue().setIfAbsent(key, owner, ttl);
        return Boolean.TRUE.equals(acquired) ? new LockHandle(key, owner) : null;
    }

    public void release(LockHandle handle) {
        redis.execute(RELEASE, Collections.singletonList(handle.key()), handle.owner());
    }

    public record LockHandle(String key, String owner) {}
}
