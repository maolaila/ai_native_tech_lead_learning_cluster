package com.example.minicommerce.identity.domain;

/**
 * 账户可以选择的角色：普通用户、管理员和客服。
 *
 * <p><strong>作用：</strong>账户可以选择的角色：普通用户、管理员和客服。
 *
 * <p><strong>为什么：</strong>角色不是某笔订单的所有权；客服能查单不等于能替用户付款，具体动作仍由服务端检查。
 *
 * <p><strong>对应文档：</strong> {@code 05_auth_security/01_Session_Cookie_Token.md}、 {@code
 * 05_auth_security/02_RBAC与对象级权限.md}、 {@code 05_auth_security/03_Web常见攻击.md}。
 */
public enum UserRole {
    USER,
    ADMIN,
    SUPPORT
}
