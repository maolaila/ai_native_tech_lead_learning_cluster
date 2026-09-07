package com.example.minicommerce.notification.infrastructure;

import org.springframework.data.jpa.repository.JpaRepository;

/**
 * 通知模块的基础设施适配层：{@code PointsLedgerRepository}。
 *
 * <p><strong>作用：</strong>声明数据库查询或更新能力，由 Spring Data 创建实现；它不负责 Redis、RabbitMQ，也不决定整个业务流程。
 *
 * <p><strong>为什么：</strong>数据库表和框架会变化；隔离适配器可以避免这些变化扩散到业务规则和 API 契约。
 *
 * <p><strong>对应文档：</strong> {@code 07_rabbitmq/01_同步异步与事件边界.md}、 {@code
 * 07_rabbitmq/04_幂等与Outbox.md}。
 */
public interface PointsLedgerRepository extends JpaRepository<PointsLedgerEntity, Long> {}
