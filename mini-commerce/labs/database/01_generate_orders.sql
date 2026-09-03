-- psql -v order_count=1000000 -f 01_generate_orders.sql
\set ON_ERROR_STOP on
\if :{?order_count}\else \set order_count 100000 \endif
insert into orders(id,order_number,user_id,status,subtotal,discount,total_amount,currency,created_at,updated_at,version)
select gen_random_uuid(),'LAB-'||g,(select min(id) from app_users),case when g%5=0 then 'PAID' else 'PENDING_PAYMENT' end,
 1000,0,1000,'JPY',now()-(g||' seconds')::interval,now(),0 from generate_series(1,:order_count) g;
analyze orders;
