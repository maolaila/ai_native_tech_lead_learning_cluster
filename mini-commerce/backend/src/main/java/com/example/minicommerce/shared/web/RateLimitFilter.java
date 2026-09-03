package com.example.minicommerce.shared.web;

import com.example.minicommerce.shared.error.ErrorCode;
import com.example.minicommerce.shared.redis.RateLimitService;
import com.example.minicommerce.shared.security.UserPrincipal;
import com.fasterxml.jackson.databind.ObjectMapper;
import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.time.Duration;
import java.util.Map;
import org.slf4j.MDC;
import org.springframework.http.MediaType;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;

/** 对应文档：06_redis/04_限流_Session与分布式锁.md、05_auth_security/03_Web常见攻击.md。 */
@Component
public class RateLimitFilter extends OncePerRequestFilter {
    private final RateLimitService limits;
    private final ObjectMapper json;

    public RateLimitFilter(RateLimitService limits, ObjectMapper json) {
        this.limits = limits;
        this.json = json;
    }

    @Override
    protected void doFilterInternal(
            HttpServletRequest request, HttpServletResponse response, FilterChain chain)
            throws ServletException, IOException {
        String path = request.getRequestURI();
        boolean login = path.equals("/api/auth/login") && request.getMethod().equals("POST");
        boolean createOrder = path.equals("/api/orders") && request.getMethod().equals("POST");
        if (!login && !createOrder) {
            chain.doFilter(request, response);
            return;
        }

        Object principal =
                SecurityContextHolder.getContext().getAuthentication() == null
                        ? null
                        : SecurityContextHolder.getContext().getAuthentication().getPrincipal();
        String identity =
                principal instanceof UserPrincipal p
                        ? "user:" + p.id()
                        : "ip:" + request.getRemoteAddr();
        int limit = login ? 8 : 20;
        boolean allowed =
                limits.allow("rate:" + path + ":" + identity, limit, Duration.ofMinutes(1), !login);
        if (!allowed) {
            response.setStatus(429);
            response.setHeader("Retry-After", "60");
            response.setContentType(MediaType.APPLICATION_JSON_VALUE);
            json.writeValue(
                    response.getOutputStream(),
                    Map.of(
                            "code",
                            ErrorCode.RATE_LIMITED.name(),
                            "message",
                            "请求过于频繁",
                            "traceId",
                            String.valueOf(MDC.get("traceId"))));
            return;
        }
        chain.doFilter(request, response);
    }
}
