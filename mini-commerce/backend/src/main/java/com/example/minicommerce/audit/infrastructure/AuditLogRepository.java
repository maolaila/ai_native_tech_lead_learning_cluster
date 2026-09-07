package com.example.minicommerce.audit.infrastructure;

import org.springframework.data.jpa.repository.JpaRepository;

/**
 * 把审计记录追加到 audit_log 表。
 *
 * <p><strong>作用：</strong>把审计记录追加到 audit_log 表。
 *
 * <p><strong>为什么：</strong>审计是业务事实的一部分，调用方应明确让它加入哪个事务；有这张表不等于已经具备防篡改审计系统。
 *
 * <p><strong>对应文档：</strong> {@code 02_backend_spring/05_日志_配置与健康检查.md}、 {@code
 * 05_auth_security/02_RBAC与对象级权限.md}、 {@code 10_observability/01_结构化日志与关联ID.md}。
 */
public interface AuditLogRepository extends JpaRepository<AuditLogEntity, Long> {}
