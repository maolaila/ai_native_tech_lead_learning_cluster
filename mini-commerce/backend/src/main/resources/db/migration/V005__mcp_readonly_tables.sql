-- 角色由本地 PostgreSQL 初始化脚本创建；测试数据库可能没有这个角色。
-- 只授权四张教学业务表，不授予账户、密码哈希、Refresh Token 或全部未来表的权限。
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'commerce_readonly') THEN
        GRANT SELECT ON products, inventory, orders, order_items TO commerce_readonly;
    END IF;
END
$$;
