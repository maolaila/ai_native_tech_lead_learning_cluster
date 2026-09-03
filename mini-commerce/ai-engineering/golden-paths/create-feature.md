# Golden Path：新增业务功能

1. 读取相关学习章节、领域规则、模块公开接口和现有回归测试。
2. 写清 Actor、业务不变量、状态转换、失败方式和不在范围。
3. 先提交领域测试；涉及数据时新增 Flyway Migration，禁止改写旧 Migration。
4. 实现顺序：Domain → Application → Infrastructure → API。
5. 检查对象级授权、幂等、并发、外部调用超时、日志和指标。
6. 运行 Unit、Integration、API、Architecture 与安全门禁。
7. 输出改动、兼容性、数据风险、测试证据、回滚/前滚方案和未验证假设。

禁止：删除失败测试迎合实现；让 Controller 直接操作 Repository；让 Agent 写生产数据库。
