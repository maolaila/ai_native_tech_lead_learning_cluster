from __future__ import annotations

import hashlib
import json
import py_compile
import shutil
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
PROJECT = REPO / "mini-commerce"
EXCLUDED = {".git", "target", ".pytest_cache", "__pycache__", ".terraform"}


def included(path: Path) -> bool:
    return path.is_file() and not any(part in EXCLUDED for part in path.parts)


for cache in PROJECT.rglob("__pycache__"):
    if cache.is_dir():
        shutil.rmtree(cache)

for source in (PROJECT / "mcp-server/src").rglob("*.py"):
    py_compile.compile(str(source), doraise=True)
for source in (PROJECT / "mcp-server/tests").rglob("*.py"):
    py_compile.compile(str(source), doraise=True)
for cache in PROJECT.rglob("__pycache__"):
    if cache.is_dir():
        shutil.rmtree(cache)

required = [
    "README.md",
    "MANIFEST.md",
    "mini-commerce/README.md",
    "mini-commerce/backend/pom.xml",
    "mini-commerce/backend/src/main/java/com/example/minicommerce/order/application/CreateOrderService.java",
    "mini-commerce/backend/src/main/java/com/example/minicommerce/payment/application/PaymentOrchestrator.java",
    "mini-commerce/backend/src/main/java/com/example/minicommerce/refund/application/RefundOrchestrator.java",
    "mini-commerce/backend/src/main/java/com/example/minicommerce/messaging/application/OutboxPublisher.java",
    "mini-commerce/backend/src/main/resources/db/migration/V001__baseline.sql",
    "mini-commerce/backend/src/main/resources/db/migration/V003__refunds.sql",
    "mini-commerce/backend/src/test/java/com/example/minicommerce/inventory/InventoryConcurrencyIT.java",
    "mini-commerce/backend/src/test/java/com/example/minicommerce/order/OrderObjectAuthorizationIT.java",
    "mini-commerce/mcp-server/src/mini_commerce_mcp/server.py",
    "mini-commerce/compose.yaml",
    "mini-commerce/infra/nginx/nginx.conf",
    "mini-commerce/infra/aws/terraform/main.tf",
    "mini-commerce/api/openapi.yaml",
    "mini-commerce/docs/generated/document-code-map.json",
]
missing = [path for path in required if not (REPO / path).exists()]
if missing:
    raise SystemExit("缺少最终交付文件：" + ", ".join(missing))

project_files = sorted(path for path in PROJECT.rglob("*") if included(path))
project_hashes = {
    path.relative_to(PROJECT).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
    for path in project_files
}
project_manifest = {
    "generatedAt": datetime.now(timezone.utc).isoformat(),
    "fileCount": len(project_files),
    "javaMainFiles": len(list((PROJECT / "backend/src/main/java").rglob("*.java"))),
    "javaTestFiles": len(list((PROJECT / "backend/src/test/java").rglob("*.java"))),
    "migrations": sorted(path.name for path in (PROJECT / "backend/src/main/resources/db/migration").glob("*.sql")),
    "documentMappingEntries": len(json.loads((PROJECT / "docs/generated/document-code-map.json").read_text(encoding="utf-8"))["entries"]),
    "sha256": project_hashes,
}
(PROJECT / "DELIVERY-MANIFEST.json").write_text(
    json.dumps(project_manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

all_files = sorted(path for path in REPO.rglob("*") if included(path) and path.name != "MANIFEST.md")
aggregate = hashlib.sha256()
for path in all_files:
    relative = path.relative_to(REPO).as_posix()
    aggregate.update(relative.encode("utf-8"))
    aggregate.update(b"\0")
    aggregate.update(hashlib.sha256(path.read_bytes()).digest())

counts = {
    "files": len(all_files),
    "markdown": sum(path.suffix.lower() == ".md" for path in all_files),
    "java": sum(path.suffix.lower() == ".java" for path in all_files),
    "sql": sum(path.suffix.lower() == ".sql" for path in all_files),
    "python": sum(path.suffix.lower() == ".py" for path in all_files),
    "yaml": sum(path.suffix.lower() in {".yml", ".yaml"} for path in all_files),
}
(REPO / "MANIFEST.md").write_text(f'''# 文档集群与完整工程联合清单

> 原始纯文档版本及其原始哈希保存在分支 `backup/docs-only-2026-09-03`。
> 当前清单在所有业务、测试、运行和安全修订后重新生成；不包含 `.git`、构建产物、Terraform 下载目录和本文件自身。

- 生成时间：{datetime.now(timezone.utc).isoformat()}
- 总文件数：{counts['files']}
- Markdown：{counts['markdown']}
- Java：{counts['java']}
- SQL：{counts['sql']}
- Python：{counts['python']}
- YAML：{counts['yaml']}
- 工程 Java 主源码：{project_manifest['javaMainFiles']}
- 工程 Java 测试：{project_manifest['javaTestFiles']}
- Flyway Migration：{len(project_manifest['migrations'])}
- 文档章节映射条目：{project_manifest['documentMappingEntries']}
- 路径及内容聚合 SHA-256：`{aggregate.hexdigest()}`

## 内容边界

- `00_start`～`16_references`、`FULL_BOOK.md`：完整学习文档集群；
- `mini-commerce/backend`：Java 21 / Spring Boot 模块化单体；
- `mini-commerce/mcp-server`、`ai-engineering`：MCP、Rules、Golden Path、Eval；
- `mini-commerce/infra`：Docker Compose、Nginx、Prometheus/Grafana/Tempo、Kubernetes、AWS Terraform；
- `mini-commerce/labs`、`api`、`scripts`：数据库、并发、故障、接口、备份和恢复实验；
- `.github/workflows`、`mini-commerce/Jenkinsfile`：质量门禁与发布流程。

单文件工程哈希见 `mini-commerce/DELIVERY-MANIFEST.json`。
''', encoding="utf-8")

(PROJECT / "BUILD-VERIFICATION.md").write_text(f'''# 构建验证说明

生成和静态完整性检查已确认：

- 工程文件：{project_manifest['fileCount']}；
- Java 主源码：{project_manifest['javaMainFiles']}；
- Java 测试：{project_manifest['javaTestFiles']}；
- Flyway Migration：{len(project_manifest['migrations'])}；
- 文档章节映射：{project_manifest['documentMappingEntries']}；
- MCP Python 源码与测试通过 `py_compile`。

真正的 Java 编译、Testcontainers PostgreSQL、ArchUnit、MCP pytest、Docker 镜像和 Terraform 验证由 `validate-and-promote-mini-commerce-v3` 执行。只有该工作流通过后，才会生成 `VALIDATION-REPORT.md` 并把同一提交快进到 `main`。
''', encoding="utf-8")

print(json.dumps({
    "status": "delivery-finalized",
    "counts": counts,
    "project": {key: value for key, value in project_manifest.items() if key != "sha256"},
    "aggregateSha256": aggregate.hexdigest(),
}, ensure_ascii=False))
