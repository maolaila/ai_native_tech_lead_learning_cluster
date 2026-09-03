package com.example.minicommerce.messaging.infrastructure;
import java.time.*;import java.util.*;import org.springframework.jdbc.core.JdbcTemplate;import org.springframework.stereotype.Repository;import org.springframework.transaction.annotation.Transactional;
/** 多 Publisher 使用 FOR UPDATE SKIP LOCKED 领取不同批次，并使用租约恢复崩溃中的 PUBLISHING 记录。 */
@Repository public class OutboxJdbcRepository{private final JdbcTemplate jdbc;public OutboxJdbcRepository(JdbcTemplate j){jdbc=j;}
 @Transactional public List<ClaimedEvent> claim(String worker,int limit,Duration lease){String sql="""
 with picked as (
   select event_id from outbox_events
   where ((status in ('PENDING','FAILED') and next_attempt_at<=now()) or (status='PUBLISHING' and locked_until<now()))
   order by created_at for update skip locked limit ?
 )
 update outbox_events o set status='PUBLISHING',locked_by=?,locked_until=now()+(? * interval '1 millisecond'),attempt_count=attempt_count+1
 from picked where o.event_id=picked.event_id
 returning o.event_id,o.event_type,o.payload,o.attempt_count
 """;return jdbc.query(sql,(rs,n)->new ClaimedEvent(rs.getObject("event_id",UUID.class),rs.getString("event_type"),rs.getString("payload"),rs.getInt("attempt_count")),limit,worker,lease.toMillis());}
 @Transactional public void published(UUID id){jdbc.update("update outbox_events set status='PUBLISHED',published_at=now(),locked_by=null,locked_until=null,last_error=null where event_id=?",id);}
 @Transactional public void failed(UUID id,int attempt,String error){long delay=Math.min(300,1L<<Math.min(attempt,8));jdbc.update("update outbox_events set status='FAILED',next_attempt_at=now()+(? * interval '1 second'),locked_by=null,locked_until=null,last_error=? where event_id=?",delay,error.substring(0,Math.min(900,error.length())),id);}
 public record ClaimedEvent(UUID eventId,String eventType,String payload,int attemptCount){}
}
