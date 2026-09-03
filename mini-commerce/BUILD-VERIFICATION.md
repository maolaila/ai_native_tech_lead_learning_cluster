# 构建验证状态

生成器静态校验已完成：

- 工程文件：190；
- Java 主源码：113；
- Java 测试：7；
- Flyway Migration：3；
- Python MCP 源码已通过 `py_compile`；
- 文档章节映射已生成。

Java 编译、Testcontainers PostgreSQL 并发测试、MCP pytest 和 Docker Compose 校验由仓库 `mini-commerce-ci` 工作流执行。CI 没有成功前，不应把本文件理解为“所有运行时验证已通过”。
