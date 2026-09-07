package com.example.minicommerce.identity.api;

import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

/**
 * 登录、注册、刷新和登出的请求与响应数据盒子。
 *
 * <p><strong>作用：</strong>登录、注册、刷新和登出的请求与响应数据盒子。
 *
 * <p><strong>为什么：</strong>RegisterRequest 不允许用户传入 ADMIN 角色；TokenResponse
 * 也不返回密码哈希。校验注解描述输入规则，不会自行登录用户。
 *
 * <p><strong>对应文档：</strong> {@code 05_auth_security/01_Session_Cookie_Token.md}、 {@code
 * 05_auth_security/02_RBAC与对象级权限.md}、 {@code 05_auth_security/03_Web常见攻击.md}。
 */
public final class AuthDtos {
    private AuthDtos() {}

    public record RegisterRequest(
            @Email @NotBlank String email,
            @NotBlank @Size(max = 100) String displayName,
            @NotBlank @Size(min = 10, max = 100) String password) {}

    public record LoginRequest(@Email @NotBlank String email, @NotBlank String password) {}

    public record RefreshRequest(@NotBlank String refreshToken) {}

    public record LogoutRequest(@NotBlank String refreshToken) {}

    public record TokenResponse(
            String accessToken,
            String refreshToken,
            long expiresInSeconds,
            Long userId,
            String email,
            String role) {}
}
