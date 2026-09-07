-- 不修改 V001～V003：Flyway 用校验和保护已经执行过的迁移。
-- 结果未知也占用执行槽位；不能等实际重复扣款后才靠成功状态唯一约束补救。
-- 若旧演示数据已有多条未终结支付，本迁移会安全失败，需要先核对，不能随意改为失败。
create unique index ux_payment_one_active_order
    on payment_attempts(order_id) where status <> 'DECLINED';

alter table refunds drop constraint refunds_status_check;
alter table refunds add constraint refunds_status_check
    check (status in ('INITIATED', 'PROCESSING', 'SUCCEEDED', 'FAILED', 'UNKNOWN'));
create unique index ux_refund_one_active_payment
    on refunds(payment_id) where status <> 'FAILED';
