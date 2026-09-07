# 构建验证状态该如何判断

文件数、Java 文件数和迁移列表见自动更新的 DELIVERY-MANIFEST.json；清单是来源完整性信息，不是测试结果。

以当前提交的 GitHub Actions 为准：mini-commerce-ci 运行 Java/Testcontainers、MCP 测试、真实 Compose HTTP Smoke 和 Terraform 静态校验；学习资料门禁运行格式、索引一致性、相对链接和严格模式文档构建。

[正式学习说明](docs/LEARNING-READINESS.md) 记录本次复现的问题、阶段性证据以及未验证范围。不得把跳过 Docker 的测试、静态分析或镜像构建成功表述成完整运行成功。
