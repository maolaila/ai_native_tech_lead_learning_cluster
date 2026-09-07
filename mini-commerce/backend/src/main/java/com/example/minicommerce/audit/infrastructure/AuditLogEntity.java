package com.example.minicommerce.audit.infrastructure;

import jakarta.persistence.*;
import java.time.Instant;

/**
 * 保存一次业务操作的操作者、资源、前后摘要和关联编号。
 *
 * <p><strong>作用：</strong>保存一次业务操作的操作者、资源、前后摘要和关联编号。
 *
 * <p><strong>为什么：</strong>审计记录用于追查谁做过什么，不是任意内容的备份；不能把密码、Token 或完整支付数据塞进摘要。
 *
 * <p><strong>对应文档：</strong> {@code 02_backend_spring/05_日志_配置与健康检查.md}、 {@code
 * 05_auth_security/02_RBAC与对象级权限.md}、 {@code 10_observability/01_结构化日志与关联ID.md}。
 */
@Entity
@Table(
        name = "audit_log",
        indexes =
                @Index(
                        name = "ix_audit_resource",
                        columnList = "resource_type,resource_id,created_at"))
public class AuditLogEntity {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "actor_id")
    private Long actorId;

    @Column(nullable = false, length = 100)
    private String action;

    @Column(name = "resource_type", nullable = false, length = 100)
    private String resourceType;

    @Column(name = "resource_id", nullable = false, length = 100)
    private String resourceId;

    @Column(nullable = false, length = 20)
    private String result;

    @Column(name = "trace_id", length = 128)
    private String traceId;

    @Column(name = "before_json", columnDefinition = "text")
    private String beforeJson;

    @Column(name = "after_json", columnDefinition = "text")
    private String afterJson;

    @Column(name = "created_at", nullable = false)
    private Instant createdAt;

    protected AuditLogEntity() {}

    public AuditLogEntity(
            Long actorId,
            String action,
            String resourceType,
            String resourceId,
            String result,
            String traceId,
            String beforeJson,
            String afterJson,
            Instant createdAt) {
        this.actorId = actorId;
        this.action = action;
        this.resourceType = resourceType;
        this.resourceId = resourceId;
        this.result = result;
        this.traceId = traceId;
        this.beforeJson = beforeJson;
        this.afterJson = afterJson;
        this.createdAt = createdAt;
    }
}
