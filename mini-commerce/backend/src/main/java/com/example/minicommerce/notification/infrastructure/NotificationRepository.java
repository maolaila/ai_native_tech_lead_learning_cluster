package com.example.minicommerce.notification.infrastructure;

import java.util.*;
import org.springframework.data.jpa.repository.JpaRepository;

/**
 * 从 notifications 表分页读取某个用户的站内通知。
 *
 * <p><strong>作用：</strong>从 notifications 表分页读取某个用户的站内通知。
 *
 * <p><strong>为什么：</strong>按 userId 过滤要在数据库查询中完成，不能先返回所有人的消息再让客户端隐藏。
 *
 * <p><strong>对应文档：</strong> {@code 07_rabbitmq/01_同步异步与事件边界.md}、 {@code
 * 07_rabbitmq/04_幂等与Outbox.md}。
 */
public interface NotificationRepository extends JpaRepository<NotificationEntity, UUID> {
    List<NotificationEntity> findTop50ByUserIdOrderByCreatedAtDesc(Long userId);
}
