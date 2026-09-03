package com.example.minicommerce.identity.domain;

/**
 * 身份与权限模块的领域模型层：{@code UserRole}。
 *
 * <p><strong>作用：</strong>表达业务状态、行为和不变量，并尽量保持对 Spring、HTTP 与数据库实现无感。
 *
 * <p><strong>为什么：</strong>领域方法比任意 Setter 更能阻止非法状态，也使测试直接描述业务语言。
 *
 * <p><strong>对应文档：</strong> {@code 05_auth_security/01_Session_Cookie_Token.md}、 {@code
 * 05_auth_security/02_RBAC与对象级权限.md}、 {@code 05_auth_security/03_Web常见攻击.md}。
 */
public enum UserRole {
    USER,
    ADMIN,
    SUPPORT
}
