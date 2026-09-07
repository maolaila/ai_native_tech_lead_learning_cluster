package com.example.minicommerce.messaging.infrastructure;

import java.util.UUID;
import org.springframework.data.jpa.repository.JpaRepository;

/**
 * 保存待发送的业务事件到 outbox_events 表。
 *
 * <p><strong>作用：</strong>保存待发送的业务事件到 outbox_events 表。
 *
 * <p><strong>为什么：</strong>事件必须和订单等业务修改一起落库；后台领取和发布状态的更新由 OutboxJdbcRepository 负责。
 *
 * <p><strong>对应文档：</strong> {@code 07_rabbitmq/02_Exchange_Queue_Routing.md}、 {@code
 * 07_rabbitmq/03_Confirm_Ack_Retry_DLQ.md}、 {@code 07_rabbitmq/04_幂等与Outbox.md}。
 */
public interface OutboxEventRepository extends JpaRepository<OutboxEventEntity, UUID> {}
