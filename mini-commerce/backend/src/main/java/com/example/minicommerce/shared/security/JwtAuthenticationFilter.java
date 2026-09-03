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
 * 共享技术基础模块的安全边界层：{@code JwtAuthenticationFilter}。
 *
 * <p><strong>作用：</strong>负责认证凭证解析、授权和安全策略，不把前端显示状态当成权限控制。
 *
 * <p><strong>为什么：</strong>安全必须在服务端默认拒绝，并通过角色、权限和对象所有权共同判断。
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
