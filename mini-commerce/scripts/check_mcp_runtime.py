"""在 MCP 容器内验证实际最小权限、审计写入和 EXPLAIN，不读取机密内容。"""
import os
from mini_commerce_mcp import tooling

with tooling.connect_readonly(os.environ['DATABASE_READONLY_URL']) as connection:
    row = connection.execute("select current_user, has_table_privilege(current_user,'orders','SELECT'), has_table_privilege(current_user,'orders','INSERT'), has_table_privilege(current_user,'users','SELECT')").fetchone()
    assert row == ('commerce_readonly', True, False, False), row
assert tooling.explain_readonly('select id from orders limit 1')['status'] == 'ok'
assert tooling.database_schema()['data']['mode'] == 'live-readonly'
assert tooling.AUDIT.is_file(), 'audit volume is not writable by non-root runtime user'
assert not tooling.execution_enabled(), 'HTTP mode must not execute test code'
print('MCP readonly role, SQL plan, audit volume and execution boundary verified')
