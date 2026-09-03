create table refunds(
 id uuid primary key,payment_id uuid not null references payment_attempts(id),order_id uuid not null references orders(id),
 user_id bigint not null references app_users(id),idempotency_key varchar(128) not null,
 status varchar(20) not null check(status in('INITIATED','SUCCEEDED','FAILED','UNKNOWN')),
 amount numeric(19,2) not null check(amount>0),provider_reference varchar(100),last_error varchar(500),
 created_at timestamptz not null,updated_at timestamptz not null,
 constraint ux_refund_payment_key unique(payment_id,idempotency_key));
create index ix_refunds_order_created on refunds(order_id,created_at desc);
