package com.example.minicommerce.shared.security;

import com.example.minicommerce.identity.infrastructure.UserRepository;
import io.jsonwebtoken.JwtException;
import jakarta.servlet.*;
import jakarta.servlet.http.*;
import java.io.IOException;
import org.slf4j.*;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;

/**
 * 从 Authorization 请求头读取 Bearer Token，验证后找出当前用户。
 *
 * <p><strong>作用：</strong>从 Authorization 请求头读取 Bearer Token，验证后找出当前用户。
 *
 * <p><strong>为什么：</strong>认证回答“你是谁”，不在这里决定“你能否看别人的订单”。每次还读取数据库中的启用状态和角色，不能只信旧 Token 的角色。
 *
 * <p><strong>对应文档：</strong> {@code 02_backend_spring/01_请求生命周期与IoC_DI.md}、 {@code
 * 02_backend_spring/04_API设计_校验_异常与错误码.md}、 {@code 11_system_design/02_模块化单体与边界.md}。
 */
@Component
public class JwtAuthenticationFilter extends OncePerRequestFilter {
    private static final Logger log = LoggerFactory.getLogger(JwtAuthenticationFilter.class);
    private final JwtService jwt;
    private final UserRepository users;

    public JwtAuthenticationFilter(JwtService j, UserRepository u) {
        jwt = j;
        users = u;
    }

    @Override
    protected void doFilterInternal(
            HttpServletRequest request, HttpServletResponse response, FilterChain chain)
            throws ServletException, IOException {
        String header = request.getHeader("Authorization");
        if (header != null
                && header.startsWith("Bearer ")
                && SecurityContextHolder.getContext().getAuthentication() == null) {
            try {
                var claims = jwt.parse(header.substring(7));
                Number raw = claims.get("uid", Number.class);
                if (raw != null)
                    users.findById(raw.longValue())
                            .filter(user -> user.isEnabled())
                            .ifPresent(
                                    user -> {
                                        UserPrincipal principal = UserPrincipal.from(user);
                                        SecurityContextHolder.getContext()
                                                .setAuthentication(
                                                        new UsernamePasswordAuthenticationToken(
                                                                principal,
                                                                null,
                                                                principal.getAuthorities()));
                                        MDC.put("userId", String.valueOf(principal.id()));
                                    });
            } catch (JwtException | IllegalArgumentException ex) {
                log.debug("event=jwt_rejected reason={}", ex.getClass().getSimpleName());
            }
        }
        try {
            chain.doFilter(request, response);
        } finally {
            MDC.remove("userId");
        }
    }
}
