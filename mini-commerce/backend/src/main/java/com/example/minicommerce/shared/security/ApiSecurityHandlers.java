package com.example.minicommerce.shared.security;

import com.example.minicommerce.shared.error.ErrorCode;
import com.fasterxml.jackson.databind.ObjectMapper;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.util.Map;
import org.slf4j.MDC;
import org.springframework.http.MediaType;
import org.springframework.security.access.AccessDeniedException;
import org.springframework.security.core.AuthenticationException;
import org.springframework.security.web.AuthenticationEntryPoint;
import org.springframework.security.web.access.AccessDeniedHandler;
import org.springframework.stereotype.Component;

/**
 * Spring Security 的统一 JSON 错误出口。
 *
 * <p><strong>作用：</strong>把“未认证”和“已认证但无权限”转换成结构稳定的 401/403 JSON 响应， 并附带 traceId，方便前端分支处理和日志关联。
 *
 * <p><strong>为什么不能只依赖默认响应：</strong>默认安全错误可能返回 HTML，且与业务接口的错误结构不同； 统一响应能让
 * API、监控和自动测试使用稳定语义，同时避免把异常堆栈暴露给客户端。
 *
 * <p><strong>对应文档：</strong> {@code 02_backend_spring/04_API设计_校验_异常与错误码.md}、 {@code
 * 05_auth_security/02_RBAC与对象级权限.md}、 {@code 10_observability/01_结构化日志与关联ID.md}。
 */
@Component
public class ApiSecurityHandlers implements AuthenticationEntryPoint, AccessDeniedHandler {

    private final ObjectMapper json;

    public ApiSecurityHandlers(ObjectMapper json) {
        this.json = json;
    }

    /** 未提供有效身份时返回 401；401 表示“还不知道你是谁”，不是权限不足。 */
    @Override
    public void commence(
            HttpServletRequest request,
            HttpServletResponse response,
            AuthenticationException exception)
            throws IOException {
        write(response, 401, ErrorCode.AUTHENTICATION_FAILED, "需要有效登录凭证");
    }

    /** 身份已经确认但没有所需权限时返回 403。 */
    @Override
    public void handle(
            HttpServletRequest request,
            HttpServletResponse response,
            AccessDeniedException exception)
            throws IOException {
        write(response, 403, ErrorCode.ACCESS_DENIED, "没有执行该操作的权限");
    }

    private void write(HttpServletResponse response, int status, ErrorCode code, String message)
            throws IOException {
        response.setStatus(status);
        response.setContentType(MediaType.APPLICATION_JSON_VALUE);
        json.writeValue(
                response.getOutputStream(),
                Map.of(
                        "code", code.name(),
                        "message", message,
                        "traceId", String.valueOf(MDC.get("traceId"))));
    }
}
