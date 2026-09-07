package com.example.minicommerce.identity.infrastructure;

import java.util.Optional;
import org.springframework.data.jpa.repository.JpaRepository;

/**
 * 按邮箱或用户 ID 查找账户，注册时检查邮箱是否已经使用。
 *
 * <p><strong>作用：</strong>按邮箱或用户 ID 查找账户，注册时检查邮箱是否已经使用。
 *
 * <p><strong>为什么：</strong>IgnoreCase 表示忽略邮箱大小写；真正防止并发重复注册还靠数据库 lower(email) 唯一索引，不只靠先查询。
 *
 * <p><strong>对应文档：</strong> {@code 05_auth_security/01_Session_Cookie_Token.md}、 {@code
 * 05_auth_security/02_RBAC与对象级权限.md}、 {@code 05_auth_security/03_Web常见攻击.md}。
 */
public interface UserRepository extends JpaRepository<UserEntity, Long> {
    Optional<UserEntity> findByEmailIgnoreCase(String email);

    boolean existsByEmailIgnoreCase(String email);
}
