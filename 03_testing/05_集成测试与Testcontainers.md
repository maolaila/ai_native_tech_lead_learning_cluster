# 集成测试：Spring Boot、Testcontainers 与 PostgreSQL

> **所属模块：** 03 Testing
> **本文用途：** 使用真实数据库验证 Mapping、约束、事务和 Migration。
> **前置知识：** 单元测试、Docker
> **建议投入：** 阅读 4 小时，配置 8 小时

---

## 一、为什么不用纯 Mock 或 H2 代替

PostgreSQL 在 SQL、类型、JSON、索引、锁、隔离、时间和约束上可能与 H2 不同。生产使用 PostgreSQL，关键测试应使用同类数据库。

## 二、流程

```text
测试启动 PostgreSQL Container
→ 注入 URL/User/Password
→ 执行 Flyway Migration
→ 准备数据
→ 调用 Service/Repository
→ 检查真实 DB
→ 清理或回滚
```

## 三、测试范围

- `@DataJpaTest`：Repository / Mapping；
- `@SpringBootTest`：跨层用例与事务；
- 不要所有测试都加载完整上下文。

## 四、Migration 必须参与

若测试靠 ORM 自动建表、生产靠 Flyway，会出现“测试绿、生产缺列”。从空库执行真实 Migration。

## 五、数据隔离

可使用：事务回滚、清表、独立 ID、共享 Container。不要依赖测试顺序或固定公共账号。

自动回滚可能掩盖真实 Commit 后行为，因此关键提交、Outbox、锁测试应使用独立事务。

## 六、约束

调用 `save()` 后 SQL 可能尚未执行；必要时 Flush 才能观察 Unique/Foreign Key 错误。

## 七、高价值测试

```text
Given 库存 1、商品可售
When 创建订单
Then 订单/订单项存在、库存 0、金额正确、幂等记录存在
```

再让库存保存失败，断言全部回滚。

## 八、数据库事务不能回滚邮件

事务中先发邮件、后 DB 回滚，邮件无法撤回。测试应暴露这类边界，为 after-commit/Outbox 做准备。

## 九、常见错误

- 测试没跑 Migration；
- 与生产不同 DB；
- 数据共享；
- 不 Flush；
- 全部 `@SpringBootTest`；
- CI 无 Docker；
- 自动回滚掩盖提交问题。
