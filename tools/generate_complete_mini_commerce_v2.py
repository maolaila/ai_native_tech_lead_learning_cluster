from __future__ import annotations

import argparse
import hashlib
import json
import os
import py_compile
import re
import stat
import sys
from datetime import datetime, timezone
from pathlib import Path

from scaffold.backend_core_v2 import FILES as CORE
from scaffold.backend_business_v2 import FILES as BUSINESS
from scaffold.backend_platform_v2 import FILES as BACKEND_PLATFORM
from scaffold.platform_v2 import FILES as PLATFORM
from scaffold.cloud_v2 import FILES as CLOUD
from scaffold.quality_fixes_v2 import FILES as QUALITY

REPO = Path(__file__).resolve().parents[1]
PROJECT = REPO / "mini-commerce"
SOURCE_DIRS = [
    "00_start", "01_foundations", "02_backend_spring", "03_testing", "04_database_postgresql",
    "05_auth_security", "06_redis", "07_rabbitmq", "08_runtime_deployment", "09_cicd",
    "10_observability", "11_system_design", "12_cloud_aws", "13_ai_engineering_mcp",
    "14_capstone", "15_templates", "16_references", "practice",
]

MODULE_TARGETS = {
    "00_start": ["mini-commerce/README.md", "mini-commerce/docs/architecture.md", "mini-commerce/compose.yaml"],
    "01_foundations": ["mini-commerce/backend/src/main/java/com/example/minicommerce/shared/web/CorrelationIdFilter.java", "mini-commerce/compose.yaml", "mini-commerce/backend/Dockerfile"],
    "02_backend_spring": ["mini-commerce/backend/src/main/java/com/example/minicommerce", "mini-commerce/backend/src/main/resources/application.yml"],
    "03_testing": ["mini-commerce/backend/src/test", "mini-commerce/mcp-server/tests", "mini-commerce/docs/testing-strategy.md"],
    "04_database_postgresql": ["mini-commerce/backend/src/main/resources/db/migration", "mini-commerce/backend/src/main/java/com/example/minicommerce/inventory", "mini-commerce/labs/database"],
    "05_auth_security": ["mini-commerce/backend/src/main/java/com/example/minicommerce/shared/security", "mini-commerce/backend/src/main/java/com/example/minicommerce/identity", "mini-commerce/docs/security.md"],
    "06_redis": ["mini-commerce/backend/src/main/java/com/example/minicommerce/catalog/application/ProductCacheService.java", "mini-commerce/backend/src/main/java/com/example/minicommerce/shared/redis", "mini-commerce/compose.yaml"],
    "07_rabbitmq": ["mini-commerce/backend/src/main/java/com/example/minicommerce/messaging", "mini-commerce/backend/src/main/java/com/example/minicommerce/notification", "mini-commerce/docs/runbooks/rabbitmq-outbox.md"],
    "08_runtime_deployment": ["mini-commerce/backend/Dockerfile", "mini-commerce/mcp-server/Dockerfile", "mini-commerce/compose.yaml", "mini-commerce/infra/k8s"],
    "09_cicd": [".github/workflows/mini-commerce-ci.yml", "mini-commerce/docs/deployment.md", "mini-commerce/scripts"],
    "10_observability": ["mini-commerce/backend/src/main/java/com/example/minicommerce/observability", "mini-commerce/infra/observability", "mini-commerce/docs/observability.md"],
    "11_system_design": ["mini-commerce/docs/architecture.md", "mini-commerce/docs/domain-model.md", "mini-commerce/backend/src/main/java/com/example/minicommerce"],
    "12_cloud_aws": ["mini-commerce/infra/aws/terraform", "mini-commerce/infra/aws/README.md"],
    "13_ai_engineering_mcp": ["mini-commerce/mcp-server", "mini-commerce/ai-engineering", "mini-commerce/tools/check_learning_references.py"],
    "14_capstone": ["mini-commerce"],
    "15_templates": ["mini-commerce/ai-engineering/golden-paths", "mini-commerce/ai-engineering/rules", "mini-commerce/docs/runbooks"],
    "16_references": ["mini-commerce/README.md", "mini-commerce/api/mini-commerce.http", "mini-commerce/labs"],
    "practice": ["mini-commerce/compose.yaml", "mini-commerce/labs", "mini-commerce/api/mini-commerce.http"],
}

KEYWORD_TARGETS = [
    (("http", "请求", "状态码", "cors"), ["mini-commerce/backend/src/main/java/com/example/minicommerce/shared/web/CorrelationIdFilter.java", "mini-commerce/api/mini-commerce.http"]),
    (("ioc", "di", "controller", "service", "repository", "dto"), ["mini-commerce/backend/src/main/java/com/example/minicommerce"]),
    (("事务", "acid", "回滚"), ["mini-commerce/backend/src/main/java/com/example/minicommerce/order/application/CreateOrderService.java", "mini-commerce/backend/src/test/java/com/example/minicommerce/order/CreateOrderIT.java"]),
    (("库存", "超卖", "并发", "锁"), ["mini-commerce/backend/src/main/java/com/example/minicommerce/inventory", "mini-commerce/backend/src/test/java/com/example/minicommerce/inventory/InventoryConcurrencyIT.java"]),
    (("索引", "explain", "慢sql", "mvcc", "死锁"), ["mini-commerce/labs/database", "mini-commerce/backend/src/main/resources/db/migration"]),
    (("session", "cookie", "jwt", "认证", "授权", "rbac", "csrf", "xss", "ssrf"), ["mini-commerce/backend/src/main/java/com/example/minicommerce/shared/security", "mini-commerce/backend/src/main/java/com/example/minicommerce/identity"]),
    (("redis", "cache", "缓存", "限流", "击穿", "雪崩", "穿透"), ["mini-commerce/backend/src/main/java/com/example/minicommerce/catalog/application/ProductCacheService.java", "mini-commerce/backend/src/main/java/com/example/minicommerce/shared/redis"]),
    (("rabbit", "消息", "outbox", "confirm", "ack", "dlq", "幂等"), ["mini-commerce/backend/src/main/java/com/example/minicommerce/messaging", "mini-commerce/backend/src/main/java/com/example/minicommerce/notification"]),
    (("支付", "webhook", "退款"), ["mini-commerce/backend/src/main/java/com/example/minicommerce/payment", "mini-commerce/backend/src/main/java/com/example/minicommerce/refund"]),
    (("docker", "compose", "容器", "优雅关闭", "signal"), ["mini-commerce/backend/Dockerfile", "mini-commerce/compose.yaml"]),
    (("日志", "metrics", "trace", "slo", "告警", "incident"), ["mini-commerce/infra/observability", "mini-commerce/docs/observability.md", "mini-commerce/docs/runbooks/incident-response.md"]),
    (("aws", "iam", "vpc", "ecs", "rds", "s3", "cloud"), ["mini-commerce/infra/aws/terraform"]),
    (("mcp", "agent", "golden", "guardrail", "eval", "rules", "prompt injection"), ["mini-commerce/mcp-server", "mini-commerce/ai-engineering"]),
]

ROOT_README = r'''# AI-Native Tech Lead / Architect 学习文件集群 + 完整工程

本仓库包含两类互相对应的资产：

1. 根目录 `00_start`～`16_references`：完整学习文档集群；
2. [`mini-commerce/`](mini-commerce/README.md)：同一真实业务上下文中的完整工程源码。

> 原始纯文档版本已保存在分支 `backup/docs-only-2026-09-03`。当前 `main` 不删除文档，而是在文档旁加入完整工程。

## 两条学习路径

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
- [文档章节与代码逐项映射](mini-commerce/docs/generated/document-code-map.md)
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
'''

PROJECT_README = r'''# Mini Commerce 完整学习工程

这不是按章节拆开的 Hello World 集合，而是一套可运行的模块化单体。所有知识点都落在同一个电商业务：用户浏览商品、加入购物车、使用优惠券创建订单、预留库存、模拟支付、处理重复回调、异步通知和积分，并具备测试、发布、监控、云映射和 AI 工程治理。

## 技术基线

- Java 21、Spring Boot 3.5.7、Maven；
- PostgreSQL + Flyway；
- Redis：Cache Aside、Null Cache、TTL 抖动、Single Flight、Lua 限流、短期锁；
- RabbitMQ：Topic Exchange、Confirm、Retry、DLQ；
- Transactional Outbox + 幂等 Consumer；
- JWT Access/Refresh、RBAC、对象级权限、HMAC Webhook；
- Actuator、Micrometer、Prometheus、Grafana、OpenTelemetry、Tempo；
- Docker Compose、Kubernetes、AWS Terraform；
- Python MCP SDK 2.1.1、只读工具、沙箱、审计和 Eval。

## 目录

```text
backend/          Spring Boot 模块化单体、Flyway、Unit/Integration/Architecture Test
mcp-server/       MCP Server 2.x：知识检索、Schema、只读 Explain、受控测试
ai-engineering/   Rules、Golden Paths、Eval 数据集
infra/            Compose 配套、Prometheus/Grafana/Tempo、K8s、AWS Terraform
labs/             百万订单、EXPLAIN、死锁、负载实验
api/              可直接执行的 HTTP 请求集
scripts/          Smoke、备份与恢复验证
docs/             架构、领域、安全、部署、可观测性和文档映射
```

## 最值得先读的业务代码

1. `order/application/CreateOrderService.java`：完整下单事务；
2. `inventory/InventoryRepository.java`：条件原子更新防超卖；
3. `order/infrastructure/OrderEntity.java`：订单状态机；
4. `payment/PaymentOrchestrator.java`：外部副作用不放长事务；
5. `messaging/OutboxPublisher.java`：领取、Confirm、失败重试；
6. `notification/OrderPaidConsumers.java`：事务内消息去重与副作用；
7. `catalog/ProductCacheService.java`：缓存穿透/击穿/雪崩保护；
8. `shared/security/*`：认证和授权边界；
9. `mcp-server/src/mini_commerce_mcp/*`：受控 AI 工具。

## 本地运行

```bash
cp .env.example .env
docker compose --profile app up -d --build
./scripts/smoke.sh
```

默认账号仅由 `local` Profile 创建：

- `alice@example.com / Password123!`
- `admin@example.com / AdminPassword123!`

管理界面不是重点。使用 `api/mini-commerce.http`、curl 或任意 API Client 操作。

## 测试

```bash
cd backend && mvn -B verify
cd ../mcp-server && python -m pip install -e '.[dev]' && pytest -q
cd .. && python3 ai-engineering/eval/run_static_eval.py
python3 tools/check_learning_references.py
```

Testcontainers 在存在 Docker 的环境执行真实 PostgreSQL Migration、事务和库存并发测试；没有 Docker 时相关测试会明确跳过，不能把跳过宣称为通过。

## 关键设计选择

- PostgreSQL 是订单、库存、金额、支付和权限的权威事实源；Redis 不能替代它。
- 创建订单不接收客户端最终价格。
- 订单项保存历史成交快照。
- 订单创建使用数据库事务级 advisory lock + 唯一约束实现 API 幂等。
- 库存使用条件 UPDATE；不使用 JVM `synchronized` 作为多实例正确性方案。
- 外部支付调用位于数据库事务外，结果通过短事务落库。
- Outbox 解决数据库与消息双写；消费者仍需幂等。
- MCP 默认只读，不提供任意 Shell、生产写 SQL、Secret 读取或无审批部署。

完整章节映射见 `docs/generated/document-code-map.md`。
'''

PACKAGE_DOCS = {
    "identity": "05_auth_security/01_Session_Cookie_Token.md",
    "catalog": "02_backend_spring/03_DTO_Entity_Domain与映射.md",
    "inventory": "04_database_postgresql/05_并发_锁与库存超卖.md",
    "cart": "02_backend_spring/02_Controller_Service_Repository分层.md",
    "promotion": "03_testing/02_测试用例设计.md",
    "order": "02_backend_spring/06_订单模块案例.md",
    "payment": "07_rabbitmq/04_幂等与Outbox.md",
    "refund": "11_system_design/04_韧性_Timeout_Retry_Circuit.md",
    "notification": "07_rabbitmq/01_同步异步与事件边界.md",
    "messaging": "07_rabbitmq/04_幂等与Outbox.md",
    "audit": "10_observability/01_结构化日志与关联ID.md",
    "observability": "10_observability/README.md",
    "shared": "11_system_design/02_模块化单体与边界.md",
}


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    normalized = content.replace("\r\n", "\n")
    if normalized and not normalized.endswith("\n"):
        normalized += "\n"
    path.write_text(normalized, encoding="utf-8")


def targets_for(source: str, title: str) -> list[str]:
    module = source.split("/", 1)[0]
    targets = list(MODULE_TARGETS.get(module, ["mini-commerce/README.md"]))
    haystack = f"{source} {title}".lower()
    for keywords, extra in KEYWORD_TARGETS:
        if any(keyword.lower() in haystack for keyword in keywords):
            targets.extend(extra)
    # 保持顺序去重，限制到最重要的 6 个入口，避免映射成为噪声。
    return list(dict.fromkeys(targets))[:6]


def generate_mapping() -> None:
    catalog: list[dict[str, object]] = []
    for directory in SOURCE_DIRS:
        root = REPO / directory
        if not root.exists():
            continue
        for path in sorted(root.rglob("*.md")):
            relative = path.relative_to(REPO).as_posix()
            lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
            headings = [(n, m.group(2).strip()) for n, line in enumerate(lines, 1)
                        if (m := re.match(r"^(#{1,3})\s+(.+?)\s*$", line))]
            if not headings:
                headings = [(1, path.stem)]
            for line_number, title in headings:
                key = f"{relative}#{line_number}:{title}"
                catalog.append({
                    "sourceId": "SRC-" + hashlib.sha256(key.encode()).hexdigest()[:12],
                    "source": relative,
                    "line": line_number,
                    "title": title,
                    "codeTargets": targets_for(relative, title),
                })

    generated = PROJECT / "docs/generated"
    generated.mkdir(parents=True, exist_ok=True)
    write(generated / "document-code-map.json", json.dumps({
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "sourceCount": len(catalog),
        "entries": catalog,
    }, ensure_ascii=False, indent=2))
    write(generated / "source-catalog.json", json.dumps(catalog, ensure_ascii=False, indent=2))

    rows = [
        "# 文档章节与代码逐项映射",
        "",
        "> 此文件由 `tools/generate_complete_mini_commerce_v2.py` 从仓库实际 Markdown 标题生成。",
        "> 源文档仍是概念与验收标准，代码目标是同一业务工程中的实现位置，不是按章节复制 Demo。",
        "",
        f"共映射 **{len(catalog)}** 个 H1～H3 章节。机器可读版：`document-code-map.json`。",
        "",
        "| Source ID | 文档与章节 | 主要代码目标 |",
        "|---|---|---|",
    ]
    for item in catalog:
        source = str(item["source"])
        title = str(item["title"]).replace("|", "\\|")
        targets = "<br>".join(f"`{t}`" for t in item["codeTargets"])
        rows.append(f"| `{item['sourceId']}` | `{source}:{item['line']}`<br>{title} | {targets} |")
    write(generated / "document-code-map.md", "\n".join(rows))


def generate_package_docs() -> None:
    base = PROJECT / "backend/src/main/java/com/example/minicommerce"
    for package, source in PACKAGE_DOCS.items():
        target = base / package / "package-info.java"
        if target.exists():
            continue
        write(target, f'''/**
 * {package} 业务/技术模块。
 *
 * <p>主要对应文档：{source}。具体类会继续标注更精确的章节和设计原因。</p>
 */
package com.example.minicommerce.{package};
''')


def generate_manifest() -> None:
    files = [p for p in PROJECT.rglob("*") if p.is_file() and "target" not in p.parts]
    hashes = {p.relative_to(PROJECT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(files)}
    java_main = list((PROJECT / "backend/src/main/java").rglob("*.java"))
    java_test = list((PROJECT / "backend/src/test/java").rglob("*.java"))
    manifest = {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "fileCount": len(files),
        "javaMainFiles": len(java_main),
        "javaTestFiles": len(java_test),
        "migrations": sorted(p.name for p in (PROJECT / "backend/src/main/resources/db/migration").glob("*.sql")),
        "sha256": hashes,
    }
    write(PROJECT / "DELIVERY-MANIFEST.json", json.dumps(manifest, ensure_ascii=False, indent=2))
    write(PROJECT / "BUILD-VERIFICATION.md", f'''# 构建验证状态

生成器静态校验已完成：

- 工程文件：{len(files)}；
- Java 主源码：{len(java_main)}；
- Java 测试：{len(java_test)}；
- Flyway Migration：{len(manifest['migrations'])}；
- Python MCP 源码已通过 `py_compile`；
- 文档章节映射已生成。

Java 编译、Testcontainers PostgreSQL 并发测试、MCP pytest 和 Docker Compose 校验由仓库 `mini-commerce-ci` 工作流执行。CI 没有成功前，不应把本文件理解为“所有运行时验证已通过”。
''')


def validate() -> None:
    required = [
        PROJECT / "backend/pom.xml",
        PROJECT / "backend/src/main/java/com/example/minicommerce/order/application/CreateOrderService.java",
        PROJECT / "backend/src/main/java/com/example/minicommerce/payment/application/PaymentOrchestrator.java",
        PROJECT / "backend/src/main/java/com/example/minicommerce/messaging/application/OutboxPublisher.java",
        PROJECT / "backend/src/main/resources/db/migration/V001__baseline.sql",
        PROJECT / "mcp-server/src/mini_commerce_mcp/server.py",
        PROJECT / "compose.yaml",
        PROJECT / "infra/aws/terraform/main.tf",
        PROJECT / "docs/generated/document-code-map.json",
    ]
    missing = [str(p.relative_to(REPO)) for p in required if not p.exists()]
    if missing:
        raise SystemExit("缺少关键文件：" + ", ".join(missing))
    java_count = len(list((PROJECT / "backend/src").rglob("*.java")))
    if java_count < 55:
        raise SystemExit(f"Java 文件数量异常：{java_count}")
    for source in (PROJECT / "mcp-server/src").rglob("*.py"):
        py_compile.compile(str(source), doraise=True)
    for source in (PROJECT / "mcp-server/tests").rglob("*.py"):
        py_compile.compile(str(source), doraise=True)
    json.loads((PROJECT / "infra/observability/grafana/dashboards/mini-commerce.json").read_text(encoding="utf-8"))
    json.loads((PROJECT / "docs/generated/document-code-map.json").read_text(encoding="utf-8"))


def generate() -> None:
    merged: dict[str, str] = {}
    for group in (CORE, BUSINESS, BACKEND_PLATFORM, PLATFORM, CLOUD, QUALITY):
        merged.update(group)
    for relative, content in merged.items():
        write(REPO / relative, content)

    # 删除此前仅用于验证分支写权限的探针文件。
    probe = PROJECT / ".push-probe"
    if probe.exists():
        probe.unlink()

    write(REPO / "README.md", ROOT_README)
    write(PROJECT / "README.md", PROJECT_README)
    generate_package_docs()
    generate_mapping()

    for path in [PROJECT / "scripts/smoke.sh", PROJECT / "scripts/backup.sh", PROJECT / "scripts/restore-test.sh"]:
        path.chmod(path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

    validate()
    generate_manifest()
    print(json.dumps({
        "status": "generated",
        "project": str(PROJECT.relative_to(REPO)),
        "files": len(list(PROJECT.rglob("*"))),
        "java": len(list((PROJECT / "backend/src").rglob("*.java"))),
    }, ensure_ascii=False))


def check() -> None:
    validate()
    print(json.dumps({"status": "valid", "project": "mini-commerce"}, ensure_ascii=False))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    check() if args.check else generate()
