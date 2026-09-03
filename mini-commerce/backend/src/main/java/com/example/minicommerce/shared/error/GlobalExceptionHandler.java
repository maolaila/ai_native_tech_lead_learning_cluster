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
 * 全局异常处理器。
 *
 * <p><strong>作用：</strong>把 Controller 和业务层抛出的异常统一转换成 JSON 错误响应，并附加业务错误码和 {@code traceId}。
 *
 * <p><strong>大白话：</strong>各个 Controller 不需要重复写很多 {@code try/catch}。异常向上抛到这里，再由这里决定返回 400、403、409 或 500。
 *
 * <p><strong>为什么 500 不返回完整异常：</strong>堆栈、SQL 和内部类名可能泄露系统结构。客户端只收到安全提示，完整异常保留在服务端日志中。
 *
 * <p><strong>对应文档：</strong> {@code 02_backend_spring/04_API设计_校验_异常与错误码.md}、 {@code
 * 10_observability/01_结构化日志与关联ID.md}、 {@code mini-commerce/docs/SPRING-JAVA-ANNOTATIONS.md}。
 */
// @RestControllerAdvice：集中接住所有 REST Controller 抛出的异常，并返回 JSON。
@RestControllerAdvice
public class GlobalExceptionHandler {
    private static final Logger log = LoggerFactory.getLogger(GlobalExceptionHandler.class);

    /** 处理可预期的业务失败，例如库存不足、订单不存在和幂等冲突。 */
    // @ExceptionHandler：指定这个方法只处理 BusinessException。
    @ExceptionHandler(BusinessException.class)
    ResponseEntity<ProblemDetail> handleBusiness(BusinessException exception) {
        ProblemDetail problem =
                base(
                        exception.code().status(),
                        exception.getMessage(),
                        exception.code().name());
        problem.setProperty("details", exception.details());
        return ResponseEntity.status(exception.code().status()).body(problem);
    }

    /** 处理请求 DTO 上的 @NotBlank、@Positive、@Size 等校验失败。 */
    @ExceptionHandler(MethodArgumentNotValidException.class)
    ResponseEntity<ProblemDetail> handleValidation(MethodArgumentNotValidException exception) {
        List<Map<String, String>> violations =
                exception.getBindingResult().getFieldErrors().stream()
                        .map(
                                error ->
                                        Map.of(
                                                "field",
                                                error.getField(),
                                                "message",
                                                error.getDefaultMessage() == null
                                                        ? "非法值"
                                                        : error.getDefaultMessage()))
                        .toList();
        ProblemDetail problem =
                base(
                        HttpStatus.BAD_REQUEST,
                        "请求参数校验失败",
                        ErrorCode.VALIDATION_ERROR.name());
        problem.setProperty("violations", violations);
        return ResponseEntity.badRequest().body(problem);
    }

    /** 处理方法参数上的校验失败，例如路径参数或查询参数不满足约束。 */
    @ExceptionHandler(ConstraintViolationException.class)
    ResponseEntity<ProblemDetail> handleConstraint(ConstraintViolationException exception) {
        return ResponseEntity.badRequest()
                .body(
                        base(
                                HttpStatus.BAD_REQUEST,
                                exception.getMessage(),
                                ErrorCode.VALIDATION_ERROR.name()));
    }

    /** 已经确认身份，但当前用户无权执行操作时返回 403。 */
    @ExceptionHandler(AccessDeniedException.class)
    ResponseEntity<ProblemDetail> handleDenied(AccessDeniedException exception) {
        return ResponseEntity.status(HttpStatus.FORBIDDEN)
                .body(
                        base(
                                HttpStatus.FORBIDDEN,
                                "没有执行该操作的权限",
                                ErrorCode.ACCESS_DENIED.name()));
    }

    /**
     * 处理数据库唯一约束、外键等完整性冲突。
     *
     * <p>数据库错误原文只写入服务端日志，客户端收到稳定、可理解的冲突提示。
     */
    @ExceptionHandler(DataIntegrityViolationException.class)
    ResponseEntity<ProblemDetail> handleIntegrity(DataIntegrityViolationException exception) {
        log.warn(
                "event=data_integrity_conflict traceId={} root={}",
                traceId(),
                exception.getMostSpecificCause().getMessage());
        return ResponseEntity.status(HttpStatus.CONFLICT)
                .body(
                        base(
                                HttpStatus.CONFLICT,
                                "数据状态发生冲突，请刷新后重试",
                                ErrorCode.IDEMPOTENCY_CONFLICT.name()));
    }

    /**
     * 最后的安全网：处理前面没有明确分类的异常。
     *
     * <p>这不代表可以忽略未知异常。这里会记录完整服务端日志，并向客户端返回不泄露内部细节的 500。
     */
    @ExceptionHandler(Exception.class)
    ResponseEntity<ProblemDetail> handleUnknown(Exception exception) {
        log.error("event=unhandled_exception traceId={}", traceId(), exception);
        return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                .body(
                        base(
                                HttpStatus.INTERNAL_SERVER_ERROR,
                                "服务暂时不可用",
                                ErrorCode.INTERNAL_ERROR.name()));
    }

    /** 构造统一的 Problem Details 响应，避免每个异常处理方法重复拼装字段。 */
    private ProblemDetail base(HttpStatus status, String detail, String code) {
        ProblemDetail problem = ProblemDetail.forStatusAndDetail(status, detail);
        problem.setType(
                URI.create("https://mini-commerce.local/problems/" + code.toLowerCase()));
        problem.setTitle(status.getReasonPhrase());
        problem.setProperty("code", code);
        problem.setProperty("traceId", traceId());
        return problem;
    }

    /** 从当前日志上下文中取得链路编号，方便客户端报错时与服务端日志对应。 */
    private String traceId() {
        String value = MDC.get("traceId");
        return value == null ? "unavailable" : value;
    }
}
