package com.example.minicommerce.shared.error;

import jakarta.validation.ConstraintViolationException;
import java.net.URI;
import java.util.List;
import java.util.Map;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.slf4j.MDC;
import org.springframework.dao.DataIntegrityViolationException;
import org.springframework.http.HttpStatus;
import org.springframework.http.ProblemDetail;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.AccessDeniedException;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;

/**
 * 统一把异常转换成 RFC 9457 Problem Details，并附加业务 code 与 traceId。
 * 500 响应不向客户端暴露堆栈；完整异常只在服务端日志保留。
 */
@RestControllerAdvice
public class GlobalExceptionHandler {
    private static final Logger log = LoggerFactory.getLogger(GlobalExceptionHandler.class);

    @ExceptionHandler(BusinessException.class)
    ResponseEntity<ProblemDetail> handleBusiness(BusinessException ex) {
        ProblemDetail problem = base(ex.code().status(), ex.getMessage(), ex.code().name());
        problem.setProperty("details", ex.details());
        return ResponseEntity.status(ex.code().status()).body(problem);
    }

    @ExceptionHandler(MethodArgumentNotValidException.class)
    ResponseEntity<ProblemDetail> handleValidation(MethodArgumentNotValidException ex) {
        List<Map<String, String>> violations = ex.getBindingResult().getFieldErrors().stream()
            .map(e -> Map.of("field", e.getField(), "message", e.getDefaultMessage() == null ? "非法值" : e.getDefaultMessage()))
            .toList();
        ProblemDetail problem = base(HttpStatus.BAD_REQUEST, "请求参数校验失败", ErrorCode.VALIDATION_ERROR.name());
        problem.setProperty("violations", violations);
        return ResponseEntity.badRequest().body(problem);
    }

    @ExceptionHandler(ConstraintViolationException.class)
    ResponseEntity<ProblemDetail> handleConstraint(ConstraintViolationException ex) {
        return ResponseEntity.badRequest().body(base(HttpStatus.BAD_REQUEST, ex.getMessage(), ErrorCode.VALIDATION_ERROR.name()));
    }

    @ExceptionHandler(AccessDeniedException.class)
    ResponseEntity<ProblemDetail> handleDenied(AccessDeniedException ex) {
        return ResponseEntity.status(HttpStatus.FORBIDDEN)
            .body(base(HttpStatus.FORBIDDEN, "没有执行该操作的权限", ErrorCode.ACCESS_DENIED.name()));
    }

    @ExceptionHandler(DataIntegrityViolationException.class)
    ResponseEntity<ProblemDetail> handleIntegrity(DataIntegrityViolationException ex) {
        log.warn("event=data_integrity_conflict traceId={} root={}", traceId(), ex.getMostSpecificCause().getMessage());
        return ResponseEntity.status(HttpStatus.CONFLICT)
            .body(base(HttpStatus.CONFLICT, "数据状态发生冲突，请刷新后重试", ErrorCode.IDEMPOTENCY_CONFLICT.name()));
    }

    @ExceptionHandler(Exception.class)
    ResponseEntity<ProblemDetail> handleUnknown(Exception ex) {
        log.error("event=unhandled_exception traceId={}", traceId(), ex);
        return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
            .body(base(HttpStatus.INTERNAL_SERVER_ERROR, "服务暂时不可用", ErrorCode.INTERNAL_ERROR.name()));
    }

    private ProblemDetail base(HttpStatus status, String detail, String code) {
        ProblemDetail problem = ProblemDetail.forStatusAndDetail(status, detail);
        problem.setType(URI.create("https://mini-commerce.local/problems/" + code.toLowerCase()));
        problem.setTitle(status.getReasonPhrase());
        problem.setProperty("code", code);
        problem.setProperty("traceId", traceId());
        return problem;
    }

    private String traceId() {
        String value = MDC.get("traceId");
        return value == null ? "unavailable" : value;
    }
}
