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
    "build-evidence", ".venv", "node_modules",
}
TRANSIENT_PROJECT_FILES = {
    "DELIVERY-MANIFEST.json",
    "CI-FAILURE-bootstrap-v7.md",
    "CI-FAILURE-bootstrap-v6.md",
    "CI-FAILURE-bootstrap.md",
    "CI-FAILURE-v5.md",
    "CI-FAILURE-v4.md",
    "CI-FAILURE-v3.md",
}


def is_included(path: Path) -> bool:
    return path.is_file() and not any(part in TRANSIENT_DIRS for part in path.parts)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def remove_caches() -> None:
    for root in (PROJECT,):
        for name in ("__pycache__", ".pytest_cache"):
            for path in root.rglob(name):
                if path.is_dir():
                    shutil.rmtree(path)


def compile_python() -> None:
    for root in (PROJECT / "mcp-server/src", PROJECT / "mcp-server/tests", PROJECT / "ai-engineering"):
        if not root.exists():
            continue
        for source in root.rglob("*.py"):
            py_compile.compile(str(source), doraise=True)
    remove_caches()


def verify_required_files() -> None:
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


def write_build_verification(validation_exists: bool, mapping_count: int, java_main: int, java_test: int, migrations: list[str]) -> None:
    if validation_exists:
        status = "完整运行门禁已通过；证据见同目录 VALIDATION-REPORT.md"
    else:
        status = "当前只完成生成与静态检查；等待发布工作流执行 Maven、Testcontainers、Docker Smoke 与 Terraform"
    content = f"""# 构建验证说明

- 当前状态：{status}。
- Java 主源码：{java_main}；
- Java 测试：{java_test}；
- Flyway Migration：{len(migrations)}（{', '.join(migrations)}）；
- 文档章节映射：{mapping_count}；
- MCP Python 源码与测试已通过语法编译检查。

`VALIDATION-REPORT.md` 不存在时，不得宣称 Maven、真实 PostgreSQL、Docker Compose 或 Terraform 已通过。
成功报告存在时，它与源码、清单位于同一 Git 提交，并记录对应 GitHub Actions 运行。
"""
    (PROJECT / "BUILD-VERIFICATION.md").write_text(content, encoding="utf-8")


def generate_project_manifest(mapping_count: int, java_main: int, java_test: int, migrations: list[str]) -> dict[str, object]:
    project_files = sorted(
        path for path in PROJECT.rglob("*")
        if is_included(path) and path.name not in TRANSIENT_PROJECT_FILES
    )
    hashes = {path.relative_to(PROJECT).as_posix(): sha256(path) for path in project_files}
    manifest: dict[str, object] = {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "fileCount": len(project_files),
        "javaMainFiles": java_main,
        "javaTestFiles": java_test,
        "migrations": migrations,
        "documentMappingEntries": mapping_count,
        "validationReportIncluded": (PROJECT / "VALIDATION-REPORT.md").exists(),
        "sha256": hashes,
    }
    (PROJECT / "DELIVERY-MANIFEST.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return manifest


def generate_repository_manifest(project_manifest: dict[str, object]) -> tuple[dict[str, int], str]:
    all_files = sorted(
        path for path in REPO.rglob("*")
        if is_included(path) and path.name != "MANIFEST.md"
    )
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
    aggregate_hex = aggregate.hexdigest()
    content = f"""# 文档集群与完整工程联合清单

> 原始纯文档版本及其原始哈希保存在分支 `backup/docs-only-2026-09-03`。
> 当前清单排除 `.git`、构建产物、Terraform Provider 下载目录、测试缓存和 CI 临时证据目录。

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
- 路径及内容聚合 SHA-256：`{aggregate_hex}`

## 内容边界

- `00_start`～`16_references`、`FULL_BOOK.md`：完整学习文档集群；
- `mini-commerce/backend`：Java 21 / Spring Boot 模块化单体；
- `mini-commerce/mcp-server`、`ai-engineering`：MCP、Rules、Golden Path 与 Eval；
- `mini-commerce/infra`：Docker Compose、Nginx、Prometheus/Grafana/Tempo、Kubernetes 与 AWS Terraform；
- `mini-commerce/labs`、`api`、`scripts`：数据库、并发、故障、接口、备份和恢复实验；
- `.github/workflows/mini-commerce-ci.yml` 与 `mini-commerce/Jenkinsfile`：持续质量门禁。

单文件工程哈希见 `mini-commerce/DELIVERY-MANIFEST.json`。为避免自引用，根清单的聚合值排除本文件自身；工程清单也排除自身。
"""
    (REPO / "MANIFEST.md").write_text(content, encoding="utf-8")
    return counts, aggregate_hex


def main() -> None:
    remove_caches()
    compile_python()
    verify_required_files()

    mapping = json.loads((PROJECT / "docs/generated/document-code-map.json").read_text(encoding="utf-8"))
    mapping_count = len(mapping["entries"])
    java_main = len(list((PROJECT / "backend/src/main/java").rglob("*.java")))
    java_test = len(list((PROJECT / "backend/src/test/java").rglob("*.java")))
    migrations = sorted(path.name for path in (PROJECT / "backend/src/main/resources/db/migration").glob("*.sql"))

    # BUILD-VERIFICATION 必须先写，再计算单文件哈希；之后不能再改动被纳入哈希的工程文件。
    write_build_verification((PROJECT / "VALIDATION-REPORT.md").exists(), mapping_count, java_main, java_test, migrations)
    project_manifest = generate_project_manifest(mapping_count, java_main, java_test, migrations)
    counts, aggregate = generate_repository_manifest(project_manifest)

    print(json.dumps({
        "status": "delivery-finalized-v7",
        "counts": counts,
        "project": {key: value for key, value in project_manifest.items() if key != "sha256"},
        "aggregateSha256": aggregate,
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
