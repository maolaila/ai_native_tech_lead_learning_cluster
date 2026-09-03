# AI-Native Tech Lead / Architect 学习文件集群 + 完整工程

本仓库包含两类互相对应的资产：

1. 根目录 `00_start`～`16_references`：完整学习文档集群；
2. [`mini-commerce/`](mini-commerce/README.md)：同一真实业务上下文中的完整工程源码。

> 原始纯文档版本保存在分支 `backup/docs-only-2026-09-03`。当前版本不删除文档，而是在文档旁加入完整工程。

## 后端小白入口

第一次系统学习后端，不要直接打开所有 Entity 或配置文件。按下面顺序开始：

1. [后端零基础：从这里开始](mini-commerce/docs/BEGINNER-START-HERE.md)
2. [一次创建订单请求：从 HTTP 到数据库](mini-commerce/docs/REQUEST-TO-DATABASE-WALKTHROUGH.md)
3. [Spring 与 Java 注解小白词典](mini-commerce/docs/SPRING-JAVA-ANNOTATIONS.md)
4. [后端专有名词通俗词典](mini-commerce/docs/BACKEND-TERMS-PLAIN-CHINESE.md)
5. [Java 后端阅读语法速查](mini-commerce/docs/JAVA-SYNTAX-FOR-BACKEND-BEGINNERS.md)
6. [Spring 配置从零开始](mini-commerce/docs/CONFIGURATION-FROM-ZERO.md)
7. [ADHD 友好的项目学习计划](mini-commerce/docs/ADHD-FOCUSED-LEARNING-PLAN.md)
8. [后端小白常见问题](mini-commerce/docs/BEGINNER-FAQ.md)

这些材料使用固定方式解释知识点：

```text
它是什么
→ 用大白话怎样理解
→ 解决什么问题
→ 在本项目哪里使用
→ 最容易犯什么错误
```

遇到陌生词时，先查项目内注释和词典；项目内仍没有解释时，再查外部资料。

## 两条进阶学习路径

### 按文档推进

从 [`00_start/01_总路线与使用方法.md`](00_start/01_总路线与使用方法.md) 开始，每读完一个主题，到 `mini-commerce` 查找对应实现、测试、故障实验和运行配置。

### 按业务链阅读源码

```text
注册/登录
→ 商品和库存
→ 购物车
→ 创建订单（权威计价、库存预留、优惠券、快照、幂等、Outbox）
→ 模拟支付 / 重复 Webhook / 退款
→ RabbitMQ 通知与积分
→ Redis 缓存和限流
→ Docker / CI/CD / 可观测性 / AWS
→ Rules / Golden Path / MCP / Eval
```

## 关键入口

- [完整工程说明](mini-commerce/README.md)
- [完整源码阅读路线](mini-commerce/docs/CODE-READING-GUIDE.md)
- [文档章节与代码逐项映射](mini-commerce/docs/generated/document-code-map.md)
- [注解在源码中的使用位置](mini-commerce/docs/generated/annotation-usage-index.md)
- [源码可读性审计](mini-commerce/docs/generated/readability-audit.md)
- [架构说明](mini-commerce/docs/architecture.md)
- [领域不变量](mini-commerce/docs/domain-model.md)
- [测试策略](mini-commerce/docs/testing-strategy.md)
- [安全边界](mini-commerce/docs/security.md)
- [部署与回滚](mini-commerce/docs/deployment.md)
- [完整合并阅读版](FULL_BOOK.md)
- [原文档导航](SUMMARY.md)

## 一键启动

```bash
cd mini-commerce
cp .env.example .env
docker compose --profile app up -d --build
./scripts/smoke.sh
```

可选可观测性：

```bash
docker compose --profile app --profile observability up -d --build
```

前端不是本项目的学习重点，因此使用 HTTP 请求集和最小 API 闭环；后端、数据库、Redis、RabbitMQ、测试、运行、云、MCP 与 Eval 均提供实际工程文件。
