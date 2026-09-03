package com.example.minicommerce.audit.infrastructure;

import org.springframework.data.jpa.repository.JpaRepository;
public interface AuditLogRepository extends JpaRepository<AuditLogEntity, Long> {}
