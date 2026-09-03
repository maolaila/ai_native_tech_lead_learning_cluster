package com.example.minicommerce.messaging.application;
import java.util.UUID;import org.springframework.jdbc.core.JdbcTemplate;import org.springframework.stereotype.Service;
/** INSERT ... ON CONFLICT DO NOTHING 与业务副作用处于同一事务；业务失败时去重记录也回滚。 */
@Service public class ProcessedMessageService{private final JdbcTemplate jdbc;public ProcessedMessageService(JdbcTemplate j){jdbc=j;}public boolean claim(String consumer,UUID eventId){return jdbc.update("insert into processed_messages(consumer_name,event_id,processed_at) values (?,?,now()) on conflict do nothing",consumer,eventId)==1;}}
