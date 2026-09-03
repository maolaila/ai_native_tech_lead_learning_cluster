package com.example.minicommerce.notification.infrastructure;

import org.springframework.data.jpa.repository.JpaRepository;

/**
 * 通知模块的基础设施适配层：{@code PointsLedgerRepository}。
 *
 * <p><strong>作用：</strong>负责 JPA、SQL、Redis、RabbitMQ 或外部系统等技术实现，并把技术细节隔离在业务边界之外。
 *
 * <p><strong>为什么：</strong>数据库表和框架会变化；隔离适配器可以避免这些变化扩散到业务规则和 API 契约。
 *
 * <p><strong>对应文档：</strong> {@code 07_rabbitmq/01_同步异步与事件边界.md}、 {@code
 * 07_rabbitmq/04_幂等与Outbox.md}。
 */
public interface PointsLedgerRepository extends JpaRepository<PointsLedgerEntity, Long> {}
