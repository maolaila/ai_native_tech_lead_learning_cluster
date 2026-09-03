package com.example.minicommerce.identity.api;

import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

/**
 * 身份与权限模块的HTTP/API 适配层：{@code AuthDtos}。
 *
 * <p><strong>作用：</strong>负责路由、请求参数、校验、认证主体和 HTTP 响应转换，不承载核心业务规则。
 *
 * <p><strong>为什么：</strong>把 HTTP 细节留在系统边界，应用服务才能脱离 Web 框架测试和复用。
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
