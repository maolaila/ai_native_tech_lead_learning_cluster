from __future__ import annotations

# 本文件由学习工程生成器使用。它不是业务运行时代码；保留它是为了让工程骨架可审计、可重建。
FILES: dict[str, str] = {
"mini-commerce/backend/pom.xml": r'''<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 https://maven.apache.org/xsd/maven-4.0.0.xsd">
  <modelVersion>4.0.0</modelVersion>
  <parent>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-parent</artifactId>
    <version>3.5.7</version>
    <relativePath/>
  </parent>

  <groupId>com.example</groupId>
  <artifactId>mini-commerce</artifactId>
  <version>1.0.0-SNAPSHOT</version>
  <name>mini-commerce</name>
  <description>AI-Native Tech Lead 学习集群的完整业务工程</description>

  <properties>
    <java.version>21</java.version>
    <jjwt.version>0.12.6</jjwt.version>
    <testcontainers.version>1.21.3</testcontainers.version>
    <archunit.version>1.4.1</archunit.version>
  </properties>

  <dependencyManagement>
    <dependencies>
      <dependency>
        <groupId>org.testcontainers</groupId>
        <artifactId>testcontainers-bom</artifactId>
        <version>${testcontainers.version}</version>
        <type>pom</type>
        <scope>import</scope>
      </dependency>
    </dependencies>
  </dependencyManagement>

  <dependencies>
    <dependency><groupId>org.springframework.boot</groupId><artifactId>spring-boot-starter-web</artifactId></dependency>
    <dependency><groupId>org.springframework.boot</groupId><artifactId>spring-boot-starter-data-jpa</artifactId></dependency>
    <dependency><groupId>org.springframework.boot</groupId><artifactId>spring-boot-starter-validation</artifactId></dependency>
    <dependency><groupId>org.springframework.boot</groupId><artifactId>spring-boot-starter-security</artifactId></dependency>
    <dependency><groupId>org.springframework.boot</groupId><artifactId>spring-boot-starter-data-redis</artifactId></dependency>
    <dependency><groupId>org.springframework.boot</groupId><artifactId>spring-boot-starter-amqp</artifactId></dependency>
    <dependency><groupId>org.springframework.boot</groupId><artifactId>spring-boot-starter-actuator</artifactId></dependency>
    <dependency><groupId>org.springframework.boot</groupId><artifactId>spring-boot-starter-aop</artifactId></dependency>
    <dependency><groupId>org.flywaydb</groupId><artifactId>flyway-core</artifactId></dependency>
    <dependency><groupId>org.flywaydb</groupId><artifactId>flyway-database-postgresql</artifactId></dependency>
    <dependency><groupId>org.postgresql</groupId><artifactId>postgresql</artifactId><scope>runtime</scope></dependency>
    <dependency><groupId>io.micrometer</groupId><artifactId>micrometer-registry-prometheus</artifactId></dependency>
    <dependency><groupId>io.micrometer</groupId><artifactId>micrometer-tracing-bridge-otel</artifactId></dependency>
    <dependency><groupId>io.opentelemetry</groupId><artifactId>opentelemetry-exporter-otlp</artifactId></dependency>
    <dependency><groupId>io.jsonwebtoken</groupId><artifactId>jjwt-api</artifactId><version>${jjwt.version}</version></dependency>
    <dependency><groupId>io.jsonwebtoken</groupId><artifactId>jjwt-impl</artifactId><version>${jjwt.version}</version><scope>runtime</scope></dependency>
    <dependency><groupId>io.jsonwebtoken</groupId><artifactId>jjwt-jackson</artifactId><version>${jjwt.version}</version><scope>runtime</scope></dependency>

    <dependency><groupId>org.springframework.boot</groupId><artifactId>spring-boot-starter-test</artifactId><scope>test</scope></dependency>
    <dependency><groupId>org.springframework.security</groupId><artifactId>spring-security-test</artifactId><scope>test</scope></dependency>
    <dependency><groupId>org.testcontainers</groupId><artifactId>junit-jupiter</artifactId><scope>test</scope></dependency>
    <dependency><groupId>org.testcontainers</groupId><artifactId>postgresql</artifactId><scope>test</scope></dependency>
    <dependency><groupId>org.awaitility</groupId><artifactId>awaitility</artifactId><scope>test</scope></dependency>
    <dependency><groupId>com.tngtech.archunit</groupId><artifactId>archunit-junit5</artifactId><version>${archunit.version}</version><scope>test</scope></dependency>
  </dependencies>

  <build>
    <plugins>
      <plugin><groupId>org.springframework.boot</groupId><artifactId>spring-boot-maven-plugin</artifactId></plugin>
      <plugin>
        <groupId>org.apache.maven.plugins</groupId><artifactId>maven-failsafe-plugin</artifactId>
        <executions><execution><goals><goal>integration-test</goal><goal>verify</goal></goals></execution></executions>
      </plugin>
      <plugin>
        <groupId>org.jacoco</groupId><artifactId>jacoco-maven-plugin</artifactId><version>0.8.13</version>
        <executions>
          <execution><goals><goal>prepare-agent</goal></goals></execution>
          <execution><id>report</id><phase>verify</phase><goals><goal>report</goal></goals></execution>
        </executions>
      </plugin>
    </plugins>
  </build>
</project>
''',
"mini-commerce/backend/src/main/resources/application.yml": r'''spring:
  application:
    name: mini-commerce
  datasource:
    url: ${DATABASE_URL:jdbc:postgresql://localhost:15432/commerce}
    username: ${DATABASE_USER:commerce_app}
    password: ${DATABASE_PASSWORD:commerce-local}
    hikari:
      maximum-pool-size: ${DB_POOL_MAX:12}
      minimum-idle: ${DB_POOL_MIN:2}
      connection-timeout: 1500ms
      validation-timeout: 1000ms
  jpa:
    open-in-view: false
    hibernate:
      ddl-auto: validate
    properties:
      hibernate:
        jdbc:
          time_zone: UTC
        order_inserts: true
        order_updates: true
  flyway:
    enabled: true
    locations: classpath:db/migration
  data:
    redis:
      host: ${REDIS_HOST:localhost}
      port: ${REDIS_PORT:16379}
      timeout: 500ms
      connect-timeout: 500ms
  rabbitmq:
    host: ${RABBITMQ_HOST:localhost}
    port: ${RABBITMQ_PORT:15672}
    username: ${RABBITMQ_USER:commerce}
    password: ${RABBITMQ_PASSWORD:commerce-local}
    publisher-confirm-type: correlated
    publisher-returns: true
    listener:
      simple:
        acknowledge-mode: auto
        default-requeue-rejected: false
        retry:
          enabled: true
          max-attempts: 3
          initial-interval: 500ms
          multiplier: 2
          max-interval: 5s
  lifecycle:
    timeout-per-shutdown-phase: 20s

server:
  port: ${SERVER_PORT:8080}
  shutdown: graceful
  forward-headers-strategy: framework

app:
  jwt:
    issuer: mini-commerce
    # 这里只是本地默认值。生产必须由 Secret Manager 注入，并定期轮换。
    secret: ${JWT_SECRET_BASE64:Y2hhbmdlLW1lLWNoYW5nZS1tZS1jaGFuZ2UtbWUtMzItYnl0ZXMtbWluaW11bQ==}
    access-ttl: 15m
    refresh-ttl: 14d
  payment:
    webhook-secret: ${PAYMENT_WEBHOOK_SECRET:local-webhook-secret-change-me}
    connect-timeout: 500ms
    read-timeout: 2s
  cache:
    product-ttl: 5m
    null-ttl: 30s
    ttl-jitter: 30s
  outbox:
    batch-size: 50
    lease: 30s
    publish-timeout: 3s
    poll-delay: 500ms

management:
  endpoints:
    web:
      exposure:
        include: health,info,prometheus,metrics,loggers,threaddump
  endpoint:
    health:
      probes:
        enabled: true
      show-details: when_authorized
  tracing:
    sampling:
      probability: ${TRACING_SAMPLE_PROBABILITY:1.0}
  otlp:
    tracing:
      endpoint: ${OTEL_EXPORTER_OTLP_TRACES_ENDPOINT:http://localhost:4318/v1/traces}
  observations:
    key-values:
      service: mini-commerce

logging:
  pattern:
    console: "%d{ISO8601} level=%-5level service=mini-commerce traceId=%X{traceId:-} requestId=%X{requestId:-} userId=%X{userId:-} orderId=%X{orderId:-} logger=%logger{36} msg=%msg%n"
''',
"mini-commerce/backend/src/main/resources/application-test.yml": r'''spring:
  task:
    scheduling:
      enabled: false
  rabbitmq:
    listener:
      simple:
        auto-startup: false
  jpa:
    properties:
      hibernate:
        format_sql: true
app:
  jwt:
    issuer: mini-commerce-test
    secret: Y2hhbmdlLW1lLWNoYW5nZS1tZS1jaGFuZ2UtbWUtMzItYnl0ZXMtbWluaW11bQ==
    access-ttl: 15m
    refresh-ttl: 1d
  payment:
    webhook-secret: test-webhook-secret
    connect-timeout: 100ms
    read-timeout: 200ms
  cache:
    product-ttl: 1m
    null-ttl: 5s
    ttl-jitter: 5s
  outbox:
    batch-size: 10
    lease: 5s
    publish-timeout: 1s
    poll-delay: 1h
management:
  tracing:
    sampling:
      probability: 0
''',
"mini-commerce/backend/src/main/java/com/example/minicommerce/MiniCommerceApplication.java": r'''package com.example.minicommerce;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.context.properties.ConfigurationPropertiesScan;
import org.springframework.scheduling.annotation.EnableScheduling;

/**
 * 完整工程的启动入口。
 *
 * <p>对应文档：00_start/02_长期项目_Mini_Commerce.md、
 * 08_runtime_deployment/04_进程_资源与优雅关闭.md。</p>
 *
 * <p>采用模块化单体而不是一开始拆微服务，因为订单、库存、优惠券当前共享一个强一致事务边界；
 * 先把边界、测试和可观测性做好，再根据真实负载决定是否拆分。</p>
 */
@SpringBootApplication
@ConfigurationPropertiesScan
@EnableScheduling
public class MiniCommerceApplication {
    public static void main(String[] args) {
        SpringApplication.run(MiniCommerceApplication.class, args);
    }
}
''',
"mini-commerce/backend/src/main/java/com/example/minicommerce/shared/config/AppProperties.java": r'''package com.example.minicommerce.shared.config;

import java.time.Duration;
import org.springframework.boot.context.properties.ConfigurationProperties;

/**
 * 类型化配置集中定义外部可变参数，避免业务代码到处散落字符串形式的 @Value。
 * 对应文档：02_backend_spring/05_日志_配置与健康检查.md、08_runtime_deployment/03_配置_Secret与环境.md。
 */
@ConfigurationProperties(prefix = "app")
public record AppProperties(Jwt jwt, Payment payment, Cache cache, Outbox outbox) {
    public record Jwt(String issuer, String secret, Duration accessTtl, Duration refreshTtl) {}
    public record Payment(String webhookSecret, Duration connectTimeout, Duration readTimeout) {}
    public record Cache(Duration productTtl, Duration nullTtl, Duration ttlJitter) {}
    public record Outbox(int batchSize, Duration lease, Duration publishTimeout, Duration pollDelay) {}
}
''',
"mini-commerce/backend/src/main/java/com/example/minicommerce/shared/config/ClockConfiguration.java": r'''package com.example.minicommerce.shared.config;

import java.time.Clock;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

/** 对应文档：03_testing/03_后端单元测试.md。注入 Clock 后，过期边界测试不依赖真实时间。 */
@Configuration
public class ClockConfiguration {
    @Bean
    Clock clock() {
        return Clock.systemUTC();
    }
}
''',
"mini-commerce/backend/src/main/java/com/example/minicommerce/shared/domain/Money.java": r'''package com.example.minicommerce.shared.domain;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.util.Objects;

/**
 * 金额值对象：禁止 double，且把币种和舍入规则放在同一语义对象中。
 * 对应文档：02_backend_spring/03_DTO_Entity_Domain与映射.md、04_database_postgresql/02_约束_范式与数据建模.md。
 */
public record Money(BigDecimal amount, String currency) {
    public Money {
        Objects.requireNonNull(amount, "amount");
        Objects.requireNonNull(currency, "currency");
        if (currency.length() != 3) throw new IllegalArgumentException("currency 必须是三位代码");
        amount = amount.setScale(2, RoundingMode.HALF_UP);
    }

    public static Money zero(String currency) { return new Money(BigDecimal.ZERO, currency); }

    public Money add(Money other) {
        requireSameCurrency(other);
        return new Money(amount.add(other.amount), currency);
    }

    public Money subtract(Money other) {
        requireSameCurrency(other);
        return new Money(amount.subtract(other.amount), currency);
    }

    public Money multiply(int quantity) {
        if (quantity <= 0) throw new IllegalArgumentException("quantity 必须大于 0");
        return new Money(amount.multiply(BigDecimal.valueOf(quantity)), currency);
    }

    private void requireSameCurrency(Money other) {
        if (!currency.equals(other.currency)) throw new IllegalArgumentException("币种不一致");
    }
}
''',
"mini-commerce/backend/src/main/java/com/example/minicommerce/shared/error/ErrorCode.java": r'''package com.example.minicommerce.shared.error;

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
''',
"mini-commerce/backend/src/main/java/com/example/minicommerce/shared/error/BusinessException.java": r'''package com.example.minicommerce.shared.error;

import java.util.Map;

/**
 * 可预期业务失败，不等同于系统故障。异常携带机器可读错误码和最小必要上下文。
 * 对应文档：02_backend_spring/04_API设计_校验_异常与错误码.md。
 */
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

    public ErrorCode code() { return code; }
    public Map<String, Object> details() { return details; }
}
''',
"mini-commerce/backend/src/main/java/com/example/minicommerce/shared/error/GlobalExceptionHandler.java": r'''package com.example.minicommerce.shared.error;

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
''',
"mini-commerce/backend/src/main/java/com/example/minicommerce/shared/web/CorrelationIdFilter.java": r'''package com.example.minicommerce.shared.web;

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
    protected void doFilterInternal(HttpServletRequest request, HttpServletResponse response, FilterChain chain)
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
''',
"mini-commerce/backend/src/main/java/com/example/minicommerce/shared/persistence/BaseEntity.java": r'''package com.example.minicommerce.shared.persistence;

import jakarta.persistence.Column;
import jakarta.persistence.MappedSuperclass;
import jakarta.persistence.PrePersist;
import jakarta.persistence.PreUpdate;
import java.time.Instant;

/** 统一技术审计时间；业务发生时间仍应由具体领域字段表达。 */
@MappedSuperclass
public abstract class BaseEntity {
    @Column(name = "created_at", nullable = false, updatable = false)
    protected Instant createdAt;
    @Column(name = "updated_at", nullable = false)
    protected Instant updatedAt;

    @PrePersist
    void beforeInsert() {
        Instant now = Instant.now();
        if (createdAt == null) createdAt = now;
        updatedAt = now;
    }

    @PreUpdate
    void beforeUpdate() { updatedAt = Instant.now(); }

    public Instant getCreatedAt() { return createdAt; }
    public Instant getUpdatedAt() { return updatedAt; }
}
''',
"mini-commerce/backend/src/main/java/com/example/minicommerce/identity/domain/UserRole.java": r'''package com.example.minicommerce.identity.domain;

public enum UserRole { USER, ADMIN, SUPPORT }
''',
"mini-commerce/backend/src/main/java/com/example/minicommerce/identity/infrastructure/UserEntity.java": r'''package com.example.minicommerce.identity.infrastructure;

import com.example.minicommerce.identity.domain.UserRole;
import com.example.minicommerce.shared.persistence.BaseEntity;
import jakarta.persistence.*;

/**
 * 持久化实体不直接作为 API Response，避免 passwordHash 等内部字段因序列化配置变化而泄露。
 * 对应文档：02_backend_spring/03_DTO_Entity_Domain与映射.md。
 */
@Entity
@Table(name = "app_users", uniqueConstraints = @UniqueConstraint(name = "ux_users_email", columnNames = "email"))
public class UserEntity extends BaseEntity {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    @Column(nullable = false, length = 320)
    private String email;
    @Column(name = "display_name", nullable = false, length = 100)
    private String displayName;
    @Column(name = "password_hash", nullable = false, length = 100)
    private String passwordHash;
    @Enumerated(EnumType.STRING) @Column(nullable = false, length = 20)
    private UserRole role;
    @Column(nullable = false)
    private boolean enabled = true;

    protected UserEntity() {}
    public UserEntity(String email, String displayName, String passwordHash, UserRole role) {
        this.email = email.toLowerCase(); this.displayName = displayName; this.passwordHash = passwordHash; this.role = role;
    }
    public Long getId() { return id; }
    public String getEmail() { return email; }
    public String getDisplayName() { return displayName; }
    public String getPasswordHash() { return passwordHash; }
    public UserRole getRole() { return role; }
    public boolean isEnabled() { return enabled; }
    public void disable() { enabled = false; }
}
''',
"mini-commerce/backend/src/main/java/com/example/minicommerce/identity/infrastructure/UserRepository.java": r'''package com.example.minicommerce.identity.infrastructure;

import java.util.Optional;
import org.springframework.data.jpa.repository.JpaRepository;

public interface UserRepository extends JpaRepository<UserEntity, Long> {
    Optional<UserEntity> findByEmailIgnoreCase(String email);
    boolean existsByEmailIgnoreCase(String email);
}
''',
"mini-commerce/backend/src/main/java/com/example/minicommerce/identity/infrastructure/RefreshTokenEntity.java": r'''package com.example.minicommerce.identity.infrastructure;

import jakarta.persistence.*;
import java.time.Instant;
import java.util.UUID;

@Entity
@Table(name = "refresh_tokens", indexes = @Index(name = "ix_refresh_token_hash", columnList = "token_hash", unique = true))
public class RefreshTokenEntity {
    @Id
    private UUID id;
    @Column(name = "user_id", nullable = false)
    private Long userId;
    @Column(name = "token_hash", nullable = false, length = 64)
    private String tokenHash;
    @Column(name = "expires_at", nullable = false)
    private Instant expiresAt;
    @Column(name = "revoked_at")
    private Instant revokedAt;
    @Column(name = "created_at", nullable = false)
    private Instant createdAt;

    protected RefreshTokenEntity() {}
    public RefreshTokenEntity(UUID id, Long userId, String tokenHash, Instant expiresAt, Instant createdAt) {
        this.id = id; this.userId = userId; this.tokenHash = tokenHash; this.expiresAt = expiresAt; this.createdAt = createdAt;
    }
    public UUID getId() { return id; }
    public Long getUserId() { return userId; }
    public String getTokenHash() { return tokenHash; }
    public boolean isValidAt(Instant now) { return revokedAt == null && expiresAt.isAfter(now); }
    public void revoke(Instant now) { if (revokedAt == null) revokedAt = now; }
}
''',
"mini-commerce/backend/src/main/java/com/example/minicommerce/identity/infrastructure/RefreshTokenRepository.java": r'''package com.example.minicommerce.identity.infrastructure;

import java.util.Optional;
import java.util.UUID;
import org.springframework.data.jpa.repository.JpaRepository;

public interface RefreshTokenRepository extends JpaRepository<RefreshTokenEntity, UUID> {
    Optional<RefreshTokenEntity> findByTokenHash(String tokenHash);
}
''',
"mini-commerce/backend/src/main/java/com/example/minicommerce/shared/security/UserPrincipal.java": r'''package com.example.minicommerce.shared.security;

import com.example.minicommerce.identity.domain.UserRole;
import com.example.minicommerce.identity.infrastructure.UserEntity;
import java.util.Collection;
import java.util.List;
import org.springframework.security.core.GrantedAuthority;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.userdetails.UserDetails;

public record UserPrincipal(Long id, String email, String password, UserRole role, boolean enabled) implements UserDetails {
    public static UserPrincipal from(UserEntity user) {
        return new UserPrincipal(user.getId(), user.getEmail(), user.getPasswordHash(), user.getRole(), user.isEnabled());
    }
    @Override public Collection<? extends GrantedAuthority> getAuthorities() {
        return List.of(new SimpleGrantedAuthority("ROLE_" + role.name()));
    }
    @Override public String getUsername() { return email; }
    @Override public String getPassword() { return password; }
    @Override public boolean isEnabled() { return enabled; }
}
''',
"mini-commerce/backend/src/main/java/com/example/minicommerce/shared/security/CurrentUser.java": r'''package com.example.minicommerce.shared.security;

import com.example.minicommerce.identity.domain.UserRole;
import com.example.minicommerce.shared.error.BusinessException;
import com.example.minicommerce.shared.error.ErrorCode;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Component;

/**
 * 统一取得认证主体；业务 Service 仍必须执行对象级权限检查，不能只依赖前端隐藏按钮或 USER 角色。
 * 对应文档：05_auth_security/02_RBAC与对象级权限.md。
 */
@Component
public class CurrentUser {
    public UserPrincipal require() {
        Authentication auth = SecurityContextHolder.getContext().getAuthentication();
        if (auth == null || !(auth.getPrincipal() instanceof UserPrincipal principal)) {
            throw new BusinessException(ErrorCode.AUTHENTICATION_FAILED, "需要登录");
        }
        return principal;
    }
    public boolean isAdmin() { return require().role() == UserRole.ADMIN; }
}
''',
"mini-commerce/backend/src/main/java/com/example/minicommerce/shared/security/JwtService.java": r'''package com.example.minicommerce.shared.security;

import com.example.minicommerce.identity.infrastructure.UserEntity;
import com.example.minicommerce.shared.config.AppProperties;
import io.jsonwebtoken.Claims;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.io.Decoders;
import io.jsonwebtoken.security.Keys;
import java.time.Clock;
import java.time.Instant;
import java.util.Date;
import javax.crypto.SecretKey;
import org.springframework.stereotype.Service;

/**
 * 短期 Access Token 只承载身份和角色，不放密码、私密资料或可长期依赖的业务状态。
 * 对应文档：05_auth_security/01_Session_Cookie_Token.md。
 */
@Service
public class JwtService {
    private final AppProperties properties;
    private final Clock clock;
    private final SecretKey key;

    public JwtService(AppProperties properties, Clock clock) {
        this.properties = properties;
        this.clock = clock;
        this.key = Keys.hmacShaKeyFor(Decoders.BASE64.decode(properties.jwt().secret()));
    }

    public String issue(UserEntity user) {
        Instant now = clock.instant();
        return Jwts.builder()
            .issuer(properties.jwt().issuer())
            .subject(user.getEmail())
            .claim("uid", user.getId())
            .claim("role", user.getRole().name())
            .issuedAt(Date.from(now))
            .expiration(Date.from(now.plus(properties.jwt().accessTtl())))
            .signWith(key)
            .compact();
    }

    public Claims parse(String token) {
        return Jwts.parser().requireIssuer(properties.jwt().issuer()).verifyWith(key).build()
            .parseSignedClaims(token).getPayload();
    }
}
''',
"mini-commerce/backend/src/main/java/com/example/minicommerce/shared/security/JwtAuthenticationFilter.java": r'''package com.example.minicommerce.shared.security;

import com.example.minicommerce.identity.infrastructure.UserRepository;
import io.jsonwebtoken.JwtException;
import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import java.io.IOException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.slf4j.MDC;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;

@Component
public class JwtAuthenticationFilter extends OncePerRequestFilter {
    private static final Logger log = LoggerFactory.getLogger(JwtAuthenticationFilter.class);
    private final JwtService jwtService;
    private final UserRepository users;

    public JwtAuthenticationFilter(JwtService jwtService, UserRepository users) {
        this.jwtService = jwtService; this.users = users;
    }

    @Override
    protected void doFilterInternal(HttpServletRequest request, HttpServletResponse response, FilterChain chain)
        throws ServletException, IOException {
        String header = request.getHeader("Authorization");
        if (header != null && header.startsWith("Bearer ") && SecurityContextHolder.getContext().getAuthentication() == null) {
            try {
                var claims = jwtService.parse(header.substring(7));
                Long userId = claims.get("uid", Long.class);
                users.findById(userId).filter(UserEntity -> UserEntity.isEnabled()).ifPresent(user -> {
                    UserPrincipal principal = UserPrincipal.from(user);
                    var authentication = new UsernamePasswordAuthenticationToken(principal, null, principal.getAuthorities());
                    SecurityContextHolder.getContext().setAuthentication(authentication);
                    MDC.put("userId", String.valueOf(principal.id()));
                });
            } catch (JwtException | IllegalArgumentException ex) {
                log.debug("event=jwt_rejected reason={}", ex.getClass().getSimpleName());
            }
        }
        try { chain.doFilter(request, response); }
        finally { MDC.remove("userId"); }
    }
}
''',
"mini-commerce/backend/src/main/java/com/example/minicommerce/shared/security/SecurityConfiguration.java": r'''package com.example.minicommerce.shared.security;

import com.example.minicommerce.shared.web.RateLimitFilter;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.http.HttpMethod;
import org.springframework.security.config.annotation.method.configuration.EnableMethodSecurity;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.http.SessionCreationPolicy;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.security.web.authentication.UsernamePasswordAuthenticationFilter;

/**
 * 本工程 API 使用 Bearer Token，因此关闭浏览器 Cookie 型 CSRF；若改为 Session Cookie，必须重新启用 CSRF 防护。
 * 对应文档：05_auth_security/01_Session_Cookie_Token.md、05_auth_security/03_Web常见攻击.md。
 */
@Configuration
@EnableMethodSecurity
public class SecurityConfiguration {
    @Bean
    SecurityFilterChain filterChain(HttpSecurity http, JwtAuthenticationFilter jwt, RateLimitFilter rateLimit) throws Exception {
        return http
            .csrf(csrf -> csrf.disable())
            .sessionManagement(s -> s.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/actuator/health/**", "/actuator/info").permitAll()
                .requestMatchers("/api/auth/**").permitAll()
                .requestMatchers(HttpMethod.GET, "/api/products/**").permitAll()
                .requestMatchers("/api/payments/webhooks/**").permitAll()
                .anyRequest().authenticated())
            .addFilterBefore(jwt, UsernamePasswordAuthenticationFilter.class)
            .addFilterAfter(rateLimit, JwtAuthenticationFilter.class)
            .build();
    }

    @Bean
    PasswordEncoder passwordEncoder() { return new BCryptPasswordEncoder(12); }
}
''',
"mini-commerce/backend/src/main/java/com/example/minicommerce/identity/api/AuthDtos.java": r'''package com.example.minicommerce.identity.api;

import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

public final class AuthDtos {
    private AuthDtos() {}
    public record RegisterRequest(@Email @NotBlank String email, @NotBlank @Size(max = 100) String displayName,
                                  @NotBlank @Size(min = 10, max = 100) String password) {}
    public record LoginRequest(@Email @NotBlank String email, @NotBlank String password) {}
    public record RefreshRequest(@NotBlank String refreshToken) {}
    public record LogoutRequest(@NotBlank String refreshToken) {}
    public record TokenResponse(String accessToken, String refreshToken, long expiresInSeconds,
                                Long userId, String email, String role) {}
}
''',
"mini-commerce/backend/src/main/java/com/example/minicommerce/identity/application/AuthService.java": r'''package com.example.minicommerce.identity.application;

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

    public AuthService(UserRepository users, RefreshTokenRepository refreshTokens, PasswordEncoder passwords,
                       JwtService jwt, AppProperties properties, Clock clock) {
        this.users = users; this.refreshTokens = refreshTokens; this.passwords = passwords;
        this.jwt = jwt; this.properties = properties; this.clock = clock;
    }

    @Transactional
    public TokenResponse register(RegisterRequest request) {
        String email = request.email().trim().toLowerCase();
        if (users.existsByEmailIgnoreCase(email)) {
            throw new BusinessException(ErrorCode.USER_ALREADY_EXISTS, "该邮箱已注册");
        }
        UserEntity user = users.save(new UserEntity(email, request.displayName().trim(), passwords.encode(request.password()), UserRole.USER));
        return issue(user);
    }

    @Transactional
    public TokenResponse login(LoginRequest request) {
        UserEntity user = users.findByEmailIgnoreCase(request.email().trim())
            .filter(UserEntity::isEnabled)
            .orElseThrow(() -> new BusinessException(ErrorCode.AUTHENTICATION_FAILED, "邮箱或密码错误"));
        if (!passwords.matches(request.password(), user.getPasswordHash())) {
            throw new BusinessException(ErrorCode.AUTHENTICATION_FAILED, "邮箱或密码错误");
        }
        return issue(user);
    }

    @Transactional
    public TokenResponse refresh(RefreshRequest request) {
        var now = clock.instant();
        RefreshTokenEntity existing = refreshTokens.findByTokenHash(hash(request.refreshToken()))
            .filter(token -> token.isValidAt(now))
            .orElseThrow(() -> new BusinessException(ErrorCode.REFRESH_TOKEN_INVALID, "Refresh Token 无效或已过期"));
        existing.revoke(now);
        UserEntity user = users.findById(existing.getUserId()).filter(UserEntity::isEnabled)
            .orElseThrow(() -> new BusinessException(ErrorCode.REFRESH_TOKEN_INVALID, "用户不可用"));
        return issue(user);
    }

    @Transactional
    public void logout(LogoutRequest request) {
        refreshTokens.findByTokenHash(hash(request.refreshToken())).ifPresent(t -> t.revoke(clock.instant()));
    }

    private TokenResponse issue(UserEntity user) {
        String rawRefresh = newRefreshToken();
        var now = clock.instant();
        refreshTokens.save(new RefreshTokenEntity(UUID.randomUUID(), user.getId(), hash(rawRefresh),
            now.plus(properties.jwt().refreshTtl()), now));
        return new TokenResponse(jwt.issue(user), rawRefresh, properties.jwt().accessTtl().toSeconds(),
            user.getId(), user.getEmail(), user.getRole().name());
    }

    private String newRefreshToken() {
        byte[] bytes = new byte[48]; random.nextBytes(bytes);
        return Base64.getUrlEncoder().withoutPadding().encodeToString(bytes);
    }

    private String hash(String value) {
        try {
            return HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(value.getBytes(StandardCharsets.UTF_8)));
        } catch (NoSuchAlgorithmException e) { throw new IllegalStateException(e); }
    }
}
''',
"mini-commerce/backend/src/main/java/com/example/minicommerce/identity/api/AuthController.java": r'''package com.example.minicommerce.identity.api;

import com.example.minicommerce.identity.api.AuthDtos.*;
import com.example.minicommerce.identity.application.AuthService;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.*;

/** Controller 只处理 HTTP 契约，认证规则和事务位于 Application Service。 */
@RestController
@RequestMapping("/api/auth")
public class AuthController {
    private final AuthService service;
    public AuthController(AuthService service) { this.service = service; }

    @PostMapping("/register") @ResponseStatus(HttpStatus.CREATED)
    TokenResponse register(@Valid @RequestBody RegisterRequest request) { return service.register(request); }

    @PostMapping("/login")
    TokenResponse login(@Valid @RequestBody LoginRequest request) { return service.login(request); }

    @PostMapping("/refresh")
    TokenResponse refresh(@Valid @RequestBody RefreshRequest request) { return service.refresh(request); }

    @PostMapping("/logout") @ResponseStatus(HttpStatus.NO_CONTENT)
    void logout(@Valid @RequestBody LogoutRequest request) { service.logout(request); }
}
''',
"mini-commerce/backend/src/main/java/com/example/minicommerce/shared/redis/RedisLockService.java": r'''package com.example.minicommerce.shared.redis;

import java.time.Duration;
import java.util.Collections;
import java.util.UUID;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.data.redis.core.script.DefaultRedisScript;
import org.springframework.stereotype.Service;

/**
 * 短期互斥锁仅用于缓存回源等可容错场景；库存正确性仍由 PostgreSQL 条件 UPDATE/行锁保证。
 * 对应文档：06_redis/04_限流_Session与分布式锁.md。
 */
@Service
public class RedisLockService {
    private static final DefaultRedisScript<Long> RELEASE = new DefaultRedisScript<>(
        "if redis.call('get', KEYS[1]) == ARGV[1] then return redis.call('del', KEYS[1]) else return 0 end", Long.class);
    private final StringRedisTemplate redis;
    public RedisLockService(StringRedisTemplate redis) { this.redis = redis; }

    public LockHandle tryLock(String key, Duration ttl) {
        String owner = UUID.randomUUID().toString();
        Boolean acquired = redis.opsForValue().setIfAbsent(key, owner, ttl);
        return Boolean.TRUE.equals(acquired) ? new LockHandle(key, owner) : null;
    }

    public void release(LockHandle handle) {
        redis.execute(RELEASE, Collections.singletonList(handle.key()), handle.owner());
    }

    public record LockHandle(String key, String owner) {}
}
''',
"mini-commerce/backend/src/main/java/com/example/minicommerce/shared/redis/RateLimitService.java": r'''package com.example.minicommerce.shared.redis;

import java.time.Duration;
import java.util.Collections;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.data.redis.core.script.DefaultRedisScript;
import org.springframework.stereotype.Service;

/**
 * Lua 将 INCR 与首次设置过期时间作为一个原子操作，避免并发下窗口永不过期。
 * Redis 故障策略由调用方区分：登录可保守拒绝，普通读接口可受控 Fail Open。
 */
@Service
public class RateLimitService {
    private static final Logger log = LoggerFactory.getLogger(RateLimitService.class);
    private static final DefaultRedisScript<Long> FIXED_WINDOW = new DefaultRedisScript<>(
        "local n=redis.call('incr',KEYS[1]); if n==1 then redis.call('pexpire',KEYS[1],ARGV[1]) end; return n", Long.class);
    private final StringRedisTemplate redis;
    public RateLimitService(StringRedisTemplate redis) { this.redis = redis; }

    public boolean allow(String key, int limit, Duration window, boolean failOpen) {
        try {
            Long count = redis.execute(FIXED_WINDOW, Collections.singletonList(key), String.valueOf(window.toMillis()));
            return count != null && count <= limit;
        } catch (RuntimeException ex) {
            log.warn("event=redis_rate_limit_unavailable key={} failOpen={} reason={}", key, failOpen, ex.getClass().getSimpleName());
            return failOpen;
        }
    }
}
''',
"mini-commerce/backend/src/main/java/com/example/minicommerce/shared/web/RateLimitFilter.java": r'''package com.example.minicommerce.shared.web;

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
    public RateLimitFilter(RateLimitService limits, ObjectMapper json) { this.limits = limits; this.json = json; }

    @Override
    protected void doFilterInternal(HttpServletRequest request, HttpServletResponse response, FilterChain chain)
        throws ServletException, IOException {
        String path = request.getRequestURI();
        boolean login = path.equals("/api/auth/login") && request.getMethod().equals("POST");
        boolean createOrder = path.equals("/api/orders") && request.getMethod().equals("POST");
        if (!login && !createOrder) { chain.doFilter(request, response); return; }

        Object principal = SecurityContextHolder.getContext().getAuthentication() == null ? null
            : SecurityContextHolder.getContext().getAuthentication().getPrincipal();
        String identity = principal instanceof UserPrincipal p ? "user:" + p.id() : "ip:" + request.getRemoteAddr();
        int limit = login ? 8 : 20;
        boolean allowed = limits.allow("rate:" + path + ":" + identity, limit, Duration.ofMinutes(1), !login);
        if (!allowed) {
            response.setStatus(429);
            response.setHeader("Retry-After", "60");
            response.setContentType(MediaType.APPLICATION_JSON_VALUE);
            json.writeValue(response.getOutputStream(), Map.of(
                "code", ErrorCode.RATE_LIMITED.name(), "message", "请求过于频繁", "traceId", String.valueOf(MDC.get("traceId"))));
            return;
        }
        chain.doFilter(request, response);
    }
}
''',
"mini-commerce/backend/src/main/java/com/example/minicommerce/audit/infrastructure/AuditLogEntity.java": r'''package com.example.minicommerce.audit.infrastructure;

import jakarta.persistence.*;
import java.time.Instant;

@Entity
@Table(name = "audit_log", indexes = @Index(name = "ix_audit_resource", columnList = "resource_type,resource_id,created_at"))
public class AuditLogEntity {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    @Column(name = "actor_id") private Long actorId;
    @Column(nullable = false, length = 100) private String action;
    @Column(name = "resource_type", nullable = false, length = 100) private String resourceType;
    @Column(name = "resource_id", nullable = false, length = 100) private String resourceId;
    @Column(nullable = false, length = 20) private String result;
    @Column(name = "trace_id", length = 128) private String traceId;
    @Column(name = "before_json", columnDefinition = "jsonb") private String beforeJson;
    @Column(name = "after_json", columnDefinition = "jsonb") private String afterJson;
    @Column(name = "created_at", nullable = false) private Instant createdAt;

    protected AuditLogEntity() {}
    public AuditLogEntity(Long actorId, String action, String resourceType, String resourceId, String result,
                          String traceId, String beforeJson, String afterJson, Instant createdAt) {
        this.actorId=actorId; this.action=action; this.resourceType=resourceType; this.resourceId=resourceId;
        this.result=result; this.traceId=traceId; this.beforeJson=beforeJson; this.afterJson=afterJson; this.createdAt=createdAt;
    }
}
''',
"mini-commerce/backend/src/main/java/com/example/minicommerce/audit/infrastructure/AuditLogRepository.java": r'''package com.example.minicommerce.audit.infrastructure;

import org.springframework.data.jpa.repository.JpaRepository;
public interface AuditLogRepository extends JpaRepository<AuditLogEntity, Long> {}
''',
"mini-commerce/backend/src/main/java/com/example/minicommerce/audit/application/AuditService.java": r'''package com.example.minicommerce.audit.application;

import com.example.minicommerce.audit.infrastructure.*;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.time.Clock;
import org.slf4j.MDC;
import org.springframework.stereotype.Service;

/**
 * 审计回答“谁在何时改了什么”，与可采样、可轮转的普通应用日志职责不同。
 * 对应文档：02_backend_spring/05_日志_配置与健康检查.md、10_observability/01_结构化日志与关联ID.md。
 */
@Service
public class AuditService {
    private final AuditLogRepository repository;
    private final ObjectMapper json;
    private final Clock clock;
    public AuditService(AuditLogRepository repository, ObjectMapper json, Clock clock) {
        this.repository=repository; this.json=json; this.clock=clock;
    }
    public void record(Long actorId, String action, String type, Object id, Object before, Object after) {
        repository.save(new AuditLogEntity(actorId, action, type, String.valueOf(id), "SUCCESS", MDC.get("traceId"),
            serialize(before), serialize(after), clock.instant()));
    }
    private String serialize(Object value) {
        if (value == null) return null;
        try { return json.writeValueAsString(value); }
        catch (JsonProcessingException e) { return "{\"serializationError\":true}"; }
    }
}
''',
"mini-commerce/backend/src/main/java/com/example/minicommerce/shared/transaction/AfterCommitExecutor.java": r'''package com.example.minicommerce.shared.transaction;

import org.springframework.stereotype.Component;
import org.springframework.transaction.support.TransactionSynchronization;
import org.springframework.transaction.support.TransactionSynchronizationManager;

/**
 * 仅把可重试/可补偿的非核心动作放到提交后。关键可靠异步动作仍需 Outbox，不能只依赖 afterCommit 回调。
 */
@Component
public class AfterCommitExecutor {
    public void run(Runnable action) {
        if (!TransactionSynchronizationManager.isActualTransactionActive()) { action.run(); return; }
        TransactionSynchronizationManager.registerSynchronization(new TransactionSynchronization() {
            @Override public void afterCommit() { action.run(); }
        });
    }
}
'''
}
