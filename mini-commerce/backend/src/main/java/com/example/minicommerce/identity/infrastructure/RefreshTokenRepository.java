package com.example.minicommerce.identity.infrastructure;

import java.util.Optional;
import java.util.UUID;
import org.springframework.data.jpa.repository.JpaRepository;

/**
 * 查找用于换取新登录凭证的刷新令牌记录。
 *
 * <p><strong>作用：</strong>查找用于换取新登录凭证的刷新令牌记录。
 *
 * <p><strong>为什么：</strong>按 tokenHash 查找时加数据库写锁，让两个同时刷新同一令牌的请求排队；第一个撤销旧令牌后，第二个就不能再次使用它。
 *
 * <p><strong>对应文档：</strong> {@code 05_auth_security/01_Session_Cookie_Token.md}、 {@code
 * 05_auth_security/02_RBAC与对象级权限.md}、 {@code 05_auth_security/03_Web常见攻击.md}。
 */
public interface RefreshTokenRepository extends JpaRepository<RefreshTokenEntity, UUID> {
    // 刷新和退出都要锁住同一条 Token，避免并发把一个旧 Token 轮换成两个新 Token。
    @org.springframework.data.jpa.repository.Lock(
            jakarta.persistence.LockModeType.PESSIMISTIC_WRITE)
    Optional<RefreshTokenEntity> findByTokenHash(String tokenHash);
}
