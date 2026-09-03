package com.example.minicommerce.identity.application;

import com.example.minicommerce.identity.api.AuthDtos.*;
import com.example.minicommerce.identity.domain.UserRole;
import com.example.minicommerce.identity.infrastructure.*;
import com.example.minicommerce.shared.config.AppProperties;
import com.example.minicommerce.shared.error.BusinessException;
import com.example.minicommerce.shared.error.ErrorCode;
import com.example.minicommerce.shared.security.JwtService;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.security.SecureRandom;
import java.time.Clock;
import java.util.Base64;
import java.util.HexFormat;
import java.util.UUID;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

/**
 * 登录生命周期：密码只用于验证；Access Token 短期；Refresh Token 只存哈希并在刷新时轮换。
 * 对应文档：05_auth_security/01_Session_Cookie_Token.md。
 */
@Service
public class AuthService {
    private final UserRepository users;
    private final RefreshTokenRepository refreshTokens;
    private final PasswordEncoder passwords;
    private final JwtService jwt;
    private final AppProperties properties;
    private final Clock clock;
    private final SecureRandom random = new SecureRandom();

    public AuthService(
            UserRepository users,
            RefreshTokenRepository refreshTokens,
            PasswordEncoder passwords,
            JwtService jwt,
            AppProperties properties,
            Clock clock) {
        this.users = users;
        this.refreshTokens = refreshTokens;
        this.passwords = passwords;
        this.jwt = jwt;
        this.properties = properties;
        this.clock = clock;
    }

    @Transactional
    public TokenResponse register(RegisterRequest request) {
        String email = request.email().trim().toLowerCase();
        if (users.existsByEmailIgnoreCase(email)) {
            throw new BusinessException(ErrorCode.USER_ALREADY_EXISTS, "该邮箱已注册");
        }
        UserEntity user =
                users.save(
                        new UserEntity(
                                email,
                                request.displayName().trim(),
                                passwords.encode(request.password()),
                                UserRole.USER));
        return issue(user);
    }

    @Transactional
    public TokenResponse login(LoginRequest request) {
        UserEntity user =
                users.findByEmailIgnoreCase(request.email().trim())
                        .filter(UserEntity::isEnabled)
                        .orElseThrow(
                                () ->
                                        new BusinessException(
                                                ErrorCode.AUTHENTICATION_FAILED, "邮箱或密码错误"));
        if (!passwords.matches(request.password(), user.getPasswordHash())) {
            throw new BusinessException(ErrorCode.AUTHENTICATION_FAILED, "邮箱或密码错误");
        }
        return issue(user);
    }

    @Transactional
    public TokenResponse refresh(RefreshRequest request) {
        var now = clock.instant();
        RefreshTokenEntity existing =
                refreshTokens
                        .findByTokenHash(hash(request.refreshToken()))
                        .filter(token -> token.isValidAt(now))
                        .orElseThrow(
                                () ->
                                        new BusinessException(
                                                ErrorCode.REFRESH_TOKEN_INVALID,
                                                "Refresh Token 无效或已过期"));
        existing.revoke(now);
        UserEntity user =
                users.findById(existing.getUserId())
                        .filter(UserEntity::isEnabled)
                        .orElseThrow(
                                () ->
                                        new BusinessException(
                                                ErrorCode.REFRESH_TOKEN_INVALID, "用户不可用"));
        return issue(user);
    }

    @Transactional
    public void logout(LogoutRequest request) {
        refreshTokens
                .findByTokenHash(hash(request.refreshToken()))
                .ifPresent(t -> t.revoke(clock.instant()));
    }

    private TokenResponse issue(UserEntity user) {
        String rawRefresh = newRefreshToken();
        var now = clock.instant();
        refreshTokens.save(
                new RefreshTokenEntity(
                        UUID.randomUUID(),
                        user.getId(),
                        hash(rawRefresh),
                        now.plus(properties.jwt().refreshTtl()),
                        now));
        return new TokenResponse(
                jwt.issue(user),
                rawRefresh,
                properties.jwt().accessTtl().toSeconds(),
                user.getId(),
                user.getEmail(),
                user.getRole().name());
    }

    private String newRefreshToken() {
        byte[] bytes = new byte[48];
        random.nextBytes(bytes);
        return Base64.getUrlEncoder().withoutPadding().encodeToString(bytes);
    }

    private String hash(String value) {
        try {
            return HexFormat.of()
                    .formatHex(
                            MessageDigest.getInstance("SHA-256")
                                    .digest(value.getBytes(StandardCharsets.UTF_8)));
        } catch (NoSuchAlgorithmException e) {
            throw new IllegalStateException(e);
        }
    }
}
