package com.example.minicommerce.shared.error;

import java.util.Map;

/** 可预期业务失败，不等同于系统故障。异常携带机器可读错误码和最小必要上下文。 对应文档：02_backend_spring/04_API设计_校验_异常与错误码.md。 */
public class BusinessException extends RuntimeException {
    private final ErrorCode code;
    private final Map<String, Object> details;

    public BusinessException(ErrorCode code, String message) {
        this(code, message, Map.of());
    }

    public BusinessException(ErrorCode code, String message, Map<String, Object> details) {
        super(message);
        this.code = code;
        this.details = Map.copyOf(details);
    }

    public ErrorCode code() {
        return code;
    }

    public Map<String, Object> details() {
        return details;
    }
}
