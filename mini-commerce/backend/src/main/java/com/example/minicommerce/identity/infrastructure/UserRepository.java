package com.example.minicommerce.identity.infrastructure;

import java.util.Optional;
import org.springframework.data.jpa.repository.JpaRepository;

/**
 * 身份与权限模块的基础设施适配层：{@code UserRepository}。
 *
 * <p><strong>作用：</strong>声明数据库查询或更新能力，由 Spring Data 创建实现；它不负责 Redis、RabbitMQ，也不决定整个业务流程。
 *
 * <p><strong>为什么：</strong>数据库表和框架会变化；隔离适配器可以避免这些变化扩散到业务规则和 API 契约。
 *
 * <p><strong>对应文档：</strong> {@code 05_auth_security/01_Session_Cookie_Token.md}、 {@code
 * 05_auth_security/02_RBAC与对象级权限.md}、 {@code 05_auth_security/03_Web常见攻击.md}。
 */
public interface UserRepository extends JpaRepository<UserEntity, Long> {
    Optional<UserEntity> findByEmailIgnoreCase(String email);

    boolean existsByEmailIgnoreCase(String email);
}
