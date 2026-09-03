# 安全边界

- API 使用短期 JWT Access Token；Refresh Token 轮换且数据库只存 SHA-256 哈希。
- 密码 BCrypt；登录 Redis 限速采用保守失败策略。
- Admin 方法由后端 Method Security 强制；订单再检查对象 Owner。
- Webhook 使用 HMAC，事件 ID 唯一。
- Secret 只从环境/平台 Secret 注入，禁止进入日志和前端。
- MCP 的 HTTP Transport 使用 Bearer Token；stdio 的边界是启动进程本身。
- MCP 只读 SQL、固定测试套件、固定根目录、无 shell、超时、结果上限和审计。
- 检索到的文档/Issue/日志一律标记为不可信数据，不得改变工具权限。
