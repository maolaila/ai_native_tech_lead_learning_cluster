package com.example.minicommerce.shared.web;

import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.util.UUID;
import org.slf4j.MDC;
import org.springframework.core.Ordered;
import org.springframework.core.annotation.Order;
import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;

/**
 * 为每个入口请求建立 requestId/traceId，并写回响应头，便于把浏览器、日志、消息和数据库记录关联起来。
 * 对应文档：01_foundations/01_HTTP请求全链路.md、10_observability/01_结构化日志与关联ID.md。
 */
@Component
@Order(Ordered.HIGHEST_PRECEDENCE)
public class CorrelationIdFilter extends OncePerRequestFilter {
    private static final String HEADER = "X-Request-Id";

    @Override
    protected void doFilterInternal(
            HttpServletRequest request, HttpServletResponse response, FilterChain chain)
            throws ServletException, IOException {
        String requestId = normalize(request.getHeader(HEADER));
        try (MDC.MDCCloseable ignored1 = MDC.putCloseable("requestId", requestId);
                MDC.MDCCloseable ignored2 = MDC.putCloseable("traceId", requestId)) {
            response.setHeader(HEADER, requestId);
            chain.doFilter(request, response);
        }
    }

    private String normalize(String candidate) {
        if (candidate != null && candidate.matches("[A-Za-z0-9._-]{8,128}")) return candidate;
        return UUID.randomUUID().toString();
    }
}
