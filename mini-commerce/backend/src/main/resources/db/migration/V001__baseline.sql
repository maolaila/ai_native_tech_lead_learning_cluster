create table app_users(
 id bigint generated always as identity primary key,email varchar(320) not null,display_name varchar(100) not null,
 password_hash varchar(100) not null,role varchar(20) not null check(role in('USER','ADMIN','SUPPORT')),enabled boolean not null default true,
 created_at timestamptz not null default now(),updated_at timestamptz not null default now());
create unique index ux_users_email on app_users(lower(email));

create table refresh_tokens(id uuid primary key,user_id bigint not null references app_users(id),token_hash varchar(64) not null unique,
 expires_at timestamptz not null,revoked_at timestamptz,created_at timestamptz not null);

create table products(id bigint generated always as identity primary key,sku varchar(64) not null unique,name varchar(200) not null,
 description varchar(2000) not null,price numeric(19,2) not null check(price>0),currency char(3) not null,
 status varchar(20) not null check(status in('DRAFT','PUBLISHED','ARCHIVED')),version bigint not null default 0,
 created_at timestamptz not null default now(),updated_at timestamptz not null default now());
create index ix_products_status_created on products(status,created_at desc);

create table inventory(product_id bigint primary key references products(id) on delete restrict,available integer not null check(available>=0),
 reserved integer not null default 0 check(reserved>=0),version bigint not null default 0,updated_at timestamptz not null default now());

create table carts(id bigint generated always as identity primary key,user_id bigint not null unique references app_users(id),
 created_at timestamptz not null default now(),updated_at timestamptz not null default now());
create table cart_items(id bigint generated always as identity primary key,cart_id bigint not null references carts(id) on delete cascade,
 product_id bigint not null references products(id),quantity integer not null check(quantity>0),created_at timestamptz not null default now(),
 updated_at timestamptz not null default now(),constraint ux_cart_product unique(cart_id,product_id));

create table coupons(id bigint generated always as identity primary key,code varchar(50) not null unique,type varchar(20) not null check(type in('PERCENT','FIXED')),
 value numeric(19,2) not null check(value>0),min_amount numeric(19,2) not null check(min_amount>=0),max_discount numeric(19,2),
 valid_from timestamptz not null,valid_until timestamptz not null,active boolean not null default true);
create table user_coupons(id bigint generated always as identity primary key,user_id bigint not null references app_users(id),coupon_id bigint not null references coupons(id),
 status varchar(20) not null check(status in('ISSUED','RESERVED','USED','EXPIRED')),reserved_order_id uuid,version bigint not null default 0,
 constraint ux_user_coupon unique(user_id,coupon_id));

create table orders(id uuid primary key,order_number varchar(40) not null unique,user_id bigint not null references app_users(id),
 status varchar(30) not null check(status in('PENDING_PAYMENT','PAID','FULFILLING','COMPLETED','CANCELLED','REFUNDING','REFUNDED')),
 subtotal numeric(19,2) not null check(subtotal>=0),discount numeric(19,2) not null check(discount>=0),total_amount numeric(19,2) not null check(total_amount>=0),
 currency char(3) not null,user_coupon_id bigint references user_coupons(id),payment_id uuid,created_at timestamptz not null,updated_at timestamptz not null,
 cancelled_at timestamptz,version bigint not null default 0);
create index ix_orders_user_created on orders(user_id,created_at desc,id desc);create index ix_orders_status_created on orders(status,created_at desc);
create table order_items(id uuid primary key,order_id uuid not null references orders(id) on delete restrict,product_id bigint not null references products(id),
 product_name_snapshot varchar(200) not null,sku_snapshot varchar(64) not null,unit_price_snapshot numeric(19,2) not null check(unit_price_snapshot>0),
 quantity integer not null check(quantity>0),line_total numeric(19,2) not null check(line_total>0),constraint ux_order_product unique(order_id,product_id));
create index ix_order_items_order on order_items(order_id);

create table idempotency_records(id uuid primary key,user_id bigint not null references app_users(id),idempotency_key varchar(128) not null,
 request_hash varchar(64) not null,status varchar(20) not null check(status in('PROCESSING','COMPLETED')),resource_id uuid,
 created_at timestamptz not null,expires_at timestamptz not null,constraint ux_idempotency_user_key unique(user_id,idempotency_key));

create table payment_attempts(id uuid primary key,order_id uuid not null references orders(id),user_id bigint not null references app_users(id),
 idempotency_key varchar(128) not null,request_hash varchar(64) not null,status varchar(20) not null check(status in('INITIATED','PROCESSING','SUCCEEDED','DECLINED','UNKNOWN')),
 amount numeric(19,2) not null,currency char(3) not null,provider_reference varchar(100),last_error varchar(500),processing_started_at timestamptz,
 created_at timestamptz not null,updated_at timestamptz not null,version bigint not null default 0,constraint ux_payment_user_key unique(user_id,idempotency_key));
create unique index ux_payment_success_per_order on payment_attempts(order_id) where status='SUCCEEDED';
create table payment_webhook_events(provider_event_id varchar(150) primary key,payload text not null,received_at timestamptz not null);

create table outbox_events(event_id uuid primary key,aggregate_type varchar(80) not null,aggregate_id varchar(100) not null,event_type varchar(100) not null,
 schema_version integer not null check(schema_version>0),payload text not null,status varchar(20) not null check(status in('PENDING','PUBLISHING','PUBLISHED','FAILED')),
 attempt_count integer not null default 0,next_attempt_at timestamptz not null,locked_by varchar(100),locked_until timestamptz,last_error varchar(1000),
 created_at timestamptz not null,published_at timestamptz);
create index ix_outbox_pending on outbox_events(next_attempt_at,created_at) where status in('PENDING','FAILED','PUBLISHING');
create table processed_messages(consumer_name varchar(100) not null,event_id uuid not null,processed_at timestamptz not null,primary key(consumer_name,event_id));

create table notifications(id uuid primary key,user_id bigint not null references app_users(id),type varchar(100) not null,message varchar(500) not null,
 unread boolean not null,created_at timestamptz not null);create index ix_notifications_user_created on notifications(user_id,created_at desc);
create table points_ledger(id bigint generated always as identity primary key,user_id bigint not null references app_users(id),order_id uuid not null references orders(id),
 reason varchar(50) not null,points integer not null,created_at timestamptz not null,constraint ux_points_order_reason unique(order_id,reason));
create table audit_log(id bigint generated always as identity primary key,actor_id bigint,action varchar(100) not null,resource_type varchar(100) not null,
 resource_id varchar(100) not null,result varchar(20) not null,trace_id varchar(128),before_json text,after_json text,created_at timestamptz not null);
create index ix_audit_resource on audit_log(resource_type,resource_id,created_at desc);
