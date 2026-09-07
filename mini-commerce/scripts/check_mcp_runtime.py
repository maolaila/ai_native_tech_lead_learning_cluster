"""在 MCP 容器内检查真实数据库权限，而不是仅检查配置文件中写了什么。

对应文档：mini-commerce/docs/LEARNING-READINESS.md 第 7 节。
这里故意同时检查“允许读订单”和“不允许读账号”：只读不等于可以读所有表。
"""

import os

from mini_commerce_mcp import tooling


def main() -> None:
    with tooling.connect_readonly(os.environ["DATABASE_READONLY_URL"]) as connection:
        # 表名必须与 Flyway 一致：用户表叫 app_users，不叫 users。
        # has_table_privilege 检查授权，不读取密码哈希或刷新令牌的内容。
        row = connection.execute(
            "select current_user, "
            "has_table_privilege(current_user, 'public.orders', 'SELECT'), "
            "has_table_privilege(current_user, 'public.orders', 'INSERT'), "
            "has_table_privilege(current_user, 'public.app_users', 'SELECT'), "
            "has_table_privilege(current_user, 'public.refresh_tokens', 'SELECT')"
        ).fetchone()
        assert row == ("commerce_readonly", True, False, False, False), row

    # 再调用实际工具，检查只读查询、在线表结构和非 root 进程写审计日志。
    assert tooling.explain_readonly("select id from orders limit 1")["status"] == "ok"
    assert tooling.database_schema()["data"]["mode"] == "live-readonly"
    assert tooling.AUDIT.is_file(), "audit volume is not writable by non-root runtime user"
    assert not tooling.execution_enabled(), "HTTP mode must not execute test code"
    print("MCP least-privilege database, live schema, EXPLAIN and audit verified")


if __name__ == "__main__":
    main()
