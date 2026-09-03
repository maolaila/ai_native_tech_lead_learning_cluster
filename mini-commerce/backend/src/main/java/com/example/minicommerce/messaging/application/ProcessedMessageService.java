package com.example.minicommerce.messaging.application;

import java.util.UUID;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Service;

/**
 * INSERT ... ON CONFLICT DO NOTHING 与业务副作用处于同一事务；业务失败时去重记录也回滚。
 *
 * <p><strong>对应文档：</strong> {@code 07_rabbitmq/02_Exchange_Queue_Routing.md}、 {@code
 * 07_rabbitmq/03_Confirm_Ack_Retry_DLQ.md}、 {@code 07_rabbitmq/04_幂等与Outbox.md}。
 */
@Service
public class ProcessedMessageService {
    private final JdbcTemplate jdbc;

    public ProcessedMessageService(JdbcTemplate j) {
        jdbc = j;
    }

    public boolean claim(String consumer, UUID eventId) {
        return jdbc.update(
                        "insert into processed_messages(consumer_name,event_id,processed_at) values (?,?,now()) on conflict do nothing",
                        consumer,
                        eventId)
                == 1;
    }
}
