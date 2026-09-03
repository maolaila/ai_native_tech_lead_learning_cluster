package com.example.minicommerce.shared.error;

import org.springframework.http.HttpStatus;

/** 业务错误码稳定供客户端和测试分支使用，中文 message 只用于人类阅读。 */
public enum ErrorCode {
    VALIDATION_ERROR(HttpStatus.BAD_REQUEST),
    AUTHENTICATION_FAILED(HttpStatus.UNAUTHORIZED),
    ACCESS_DENIED(HttpStatus.FORBIDDEN),
    USER_ALREADY_EXISTS(HttpStatus.CONFLICT),
    REFRESH_TOKEN_INVALID(HttpStatus.UNAUTHORIZED),
    PRODUCT_NOT_FOUND(HttpStatus.NOT_FOUND),
    PRODUCT_NOT_SELLABLE(HttpStatus.CONFLICT),
    INVENTORY_NOT_FOUND(HttpStatus.NOT_FOUND),
    INSUFFICIENT_STOCK(HttpStatus.CONFLICT),
    CART_ITEM_NOT_FOUND(HttpStatus.NOT_FOUND),
    COUPON_NOT_FOUND(HttpStatus.NOT_FOUND),
    COUPON_NOT_APPLICABLE(HttpStatus.CONFLICT),
    COUPON_ALREADY_USED(HttpStatus.CONFLICT),
    ORDER_EMPTY(HttpStatus.BAD_REQUEST),
    ORDER_NOT_FOUND(HttpStatus.NOT_FOUND),
    ORDER_NOT_CANCELLABLE(HttpStatus.CONFLICT),
    ORDER_NOT_PAYABLE(HttpStatus.CONFLICT),
    ORDER_NOT_REFUNDABLE(HttpStatus.CONFLICT),
    IDEMPOTENCY_KEY_REQUIRED(HttpStatus.BAD_REQUEST),
    IDEMPOTENCY_CONFLICT(HttpStatus.CONFLICT),
    PAYMENT_DECLINED(HttpStatus.CONFLICT),
    PAYMENT_DEPENDENCY_UNAVAILABLE(HttpStatus.SERVICE_UNAVAILABLE),
    PAYMENT_SIGNATURE_INVALID(HttpStatus.UNAUTHORIZED),
    RATE_LIMITED(HttpStatus.TOO_MANY_REQUESTS),
    INTERNAL_ERROR(HttpStatus.INTERNAL_SERVER_ERROR);

    private final HttpStatus status;
    ErrorCode(HttpStatus status) { this.status = status; }
    public HttpStatus status() { return status; }
}
