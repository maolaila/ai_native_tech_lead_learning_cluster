package com.example.minicommerce.notification.infrastructure;

import org.springframework.data.jpa.repository.JpaRepository;

/**
 * 保存付款后产生的积分流水。
 *
 * <p><strong>作用：</strong>保存付款后产生的积分流水。
 *
 * <p><strong>为什么：</strong>这里继承 JpaRepository 的 save 等方法，不必手写相同的插入 SQL；积分计算仍由消费者负责。
 *
 * <p><strong>对应文档：</strong> {@code 07_rabbitmq/01_同步异步与事件边界.md}、 {@code
 * 07_rabbitmq/04_幂等与Outbox.md}。
 */
public interface PointsLedgerRepository extends JpaRepository<PointsLedgerEntity, Long> {}
