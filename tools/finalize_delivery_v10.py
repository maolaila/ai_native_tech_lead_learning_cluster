from __future__ import annotations

import hashlib
import json
import py_compile
import shutil
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
PROJECT = REPO / "mini-commerce"
TRANSIENT_DIRS = {
    ".git", "target", ".pytest_cache", "__pycache__", ".terraform",
    "build-evidence", ".venv", "node_modules", "backups",
}
TRANSIENT_FILES = {
    "DELIVERY-MANIFEST.json",
    "CI-FAILURE-bootstrap-v10.md",
    "CI-FAILURE-bootstrap-v9.md",
    "CI-FAILURE-bootstrap-v8.md",
    "CI-FAILURE-bootstrap-v7.md",
}


def included(path: Path) -> bool:
    if not path.is_file() or any(part in TRANSIENT_DIRS for part in path.parts):
        return False
    return not any(part.endswith(".egg-info") for part in path.parts)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def remove_transient_dirs() -> None:
    for pattern in ("__pycache__", ".pytest_cache", "*.egg-info"):
        for path in PROJECT.rglob(pattern):
            if path.is_dir():
                shutil.rmtree(path)


def compile_python() -> None:
    roots = [PROJECT / "mcp-server/src", PROJECT / "mcp-server/tests", PROJECT / "ai-engineering"]
    for root in roots:
        if root.exists():
            for source in root.rglob("*.py"):
                py_compile.compile(str(source), doraise=True)
    remove_transient_dirs()


def require_delivery_files() -> None:
    required = [
        "README.md",
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
        "mini-commerce/mcp-server/tests/test_server_contract.py",
        "mini-commerce/compose.yaml",
        "mini-commerce/infra/nginx/nginx.conf",
        "mini-commerce/infra/aws/terraform/main.tf",
        "mini-commerce/api/openapi.yaml",
        "mini-commerce/docs/document-review-and-corrections.md",
        "mini-commerce/docs/code-reading-guide.md",
        "mini-commerce/docs/generated/document-code-map.json",
        ".github/workflows/mini-commerce-ci.yml",
    ]
    missing = [relative for relative in required if not (REPO / relative).exists()]
    if missing:
        raise SystemExit("缺少最终交付文件：" + ", ".join(missing))


def write_build_status(validation: bool, java_main: int, java_test: int, migrations: list[str], mapping_count: int) -> None:
    state = (
        "完整运行门禁已通过；同提交证据见 VALIDATION-REPORT.md"
        if validation else
        "仅完成生成和静态完整性检查；运行级门禁尚未形成成功报告"
    )
    (PROJECT / "BUILD-VERIFICATION.md").write_text(f'''# 构建验证说明

- 当前状态：{state}。
- Java 主源码：{java_main}；
- Java 测试：{java_test}；
- Flyway Migration：{len(migrations)}（{', '.join(migrations)}）；
- 文档章节映射：{mapping_count}；
- MCP Python 源码和测试已通过语法编译检查。

`VALIDATION-REPORT.md` 不存在时，不得宣称 Maven、Testcontainers PostgreSQL、Docker Compose Smoke 或 Terraform 已通过。
''', encoding="utf-8")


def write_project_manifest(java_main: int, java_test: int, migrations: list[str], mapping_count: int) -> dict[str, object]:
    files = sorted(
        path for path in PROJECT.rglob("*")
        if included(path) and path.name not in TRANSIENT_FILES
    )
    manifest: dict[str, object] = {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "fileCount": len(files),
        "javaMainFiles": java_main,
        "javaTestFiles": java_test,
        "migrations": migrations,
        "documentMappingEntries": mapping_count,
        "validationReportIncluded": (PROJECT / "VALIDATION-REPORT.md").exists(),
        "sha256": {path.relative_to(PROJECT).as_posix(): digest(path) for path in files},
    }
    (PROJECT / "DELIVERY-MANIFEST.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return manifest


def write_repository_manifest(project_manifest: dict[str, object]) -> tuple[dict[str, int], str]:
    files = sorted(
        path for path in REPO.rglob("*")
        if included(path) and path.name != "MANIFEST.md"
    )
    aggregate = hashlib.sha256()
    for path in files:
        aggregate.update(path.relative_to(REPO).as_posix().encode("utf-8"))
        aggregate.update(b"\0")
        aggregate.update(hashlib.sha256(path.read_bytes()).digest())
    counts = {
        "files": len(files),
        "markdown": sum(path.suffix.lower() == ".md" for path in files),
        "java": sum(path.suffix.lower() == ".java" for path in files),
        "sql": sum(path.suffix.lower() == ".sql" for path in files),
        "python": sum(path.suffix.lower() == ".py" for path in files),
        "yaml": sum(path.suffix.lower() in {".yml", ".yaml"} for path in files),
    }
    aggregate_hex = aggregate.hexdigest()
    (REPO / "MANIFEST.md").write_text(f'''# 文档集群与完整工程联合清单

> 原始纯文档版本与原始哈希保存在 `backup/docs-only-2026-09-03`。
> 当前清单排除 Git、构建输出、Terraform Provider、测试缓存、editable-install 元数据和 CI 临时证据。

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
- 文档章节映射：{project_manifest['documentMappingEntries']}
- 已包含成功验证报告：{project_manifest['validationReportIncluded']}
- 路径和内容聚合 SHA-256：`{aggregate_hex}`

## 组成

- `00_start`～`16_references` 与 `FULL_BOOK.md`：完整学习文档集群；
- `mini-commerce/backend`：Java/Spring Boot 模块化单体；
- `mini-commerce/mcp-server` 与 `ai-engineering`：MCP、Rules、Golden Path、Eval；
- `mini-commerce/infra`：Compose、Nginx、Prometheus/Grafana/Tempo、Kubernetes、AWS Terraform；
- `mini-commerce/labs`、`api`、`scripts`：数据库、并发、接口、故障、备份和恢复实验；
- `.github/workflows/mini-commerce-ci.yml` 与 `mini-commerce/Jenkinsfile`：持续质量门禁。

单文件工程哈希见 `mini-commerce/DELIVERY-MANIFEST.json`。聚合值为避免自引用而排除本文件；工程清单也排除自身。
''', encoding="utf-8")
    return counts, aggregate_hex


def main() -> None:
    remove_transient_dirs()
    compile_python()
    require_delivery_files()

    mapping_count = len(json.loads(
        (PROJECT / "docs/generated/document-code-map.json").read_text(encoding="utf-8")
    )["entries"])
    java_main = len(list((PROJECT / "backend/src/main/java").rglob("*.java")))
    java_test = len(list((PROJECT / "backend/src/test/java").rglob("*.java")))
    migrations = sorted(path.name for path in (PROJECT / "backend/src/main/resources/db/migration").glob("*.sql"))

    # 必须先写状态文件，再计算清单哈希；生成清单后不再修改被纳入哈希的文件。
    write_build_status((PROJECT / "VALIDATION-REPORT.md").exists(), java_main, java_test, migrations, mapping_count)
    project = write_project_manifest(java_main, java_test, migrations, mapping_count)
    counts, aggregate = write_repository_manifest(project)

    print(json.dumps({
        "status": "delivery-finalized-v10",
        "counts": counts,
        "project": {key: value for key, value in project.items() if key != "sha256"},
        "aggregateSha256": aggregate,
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
