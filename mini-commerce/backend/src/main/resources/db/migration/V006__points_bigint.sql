-- 积分使用 bigint，避免较大合法订单金额转换为 int 时静默溢出。
alter table points_ledger alter column points type bigint;
