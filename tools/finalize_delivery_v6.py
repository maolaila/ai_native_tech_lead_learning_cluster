from __future__ import annotations

import hashlib
import json
import py_compile
import shutil
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
PROJECT = REPO / "mini-commerce"
EXCLUDED_PARTS = {".git", "target", ".pytest_cache", "__pycache__", ".terraform", "build-evidence", ".venv"}
EXCLUDED_PROJECT_FILES = {"DELIVERY-MANIFEST.json", "CI-FAILURE-bootstrap.md", "CI-FAILURE-v5.md", "CI-FAILURE-v4.md", "CI-FAILURE-v3.md"}


def included(path: Path) -> bool:
    return path.is_file() and not any(part in EXCLUDED_PARTS for part in path.parts)


for cache in PROJECT.rglob("__pycache__"):
    if cache.is_dir(): shutil.rmtree(cache)
for source in list((PROJECT / "mcp-server/src").rglob("*.py")) + list((PROJECT / "mcp-server/tests").rglob("*.py")):
    py_compile.compile(str(source), doraise=True)
for cache in PROJECT.rglob("__pycache__"):
    if cache.is_dir(): shutil.rmtree(cache)

project_files = sorted(path for path in PROJECT.rglob("*") if included(path) and path.name not in EXCLUDED_PROJECT_FILES)
project_hashes = {
    path.relative_to(PROJECT).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
    for path in project_files
}
mapping = json.loads((PROJECT / "docs/generated/document-code-map.json").read_text(encoding="utf-8"))
project_manifest = {
    "generatedAt": datetime.now(timezone.utc).isoformat(),
    "fileCount": len(project_files),
    "javaMainFiles": len(list((PROJECT / "backend/src/main/java").rglob("*.java"))),
    "javaTestFiles": len(list((PROJECT / "backend/src/test/java").rglob("*.java"))),
    "migrations": sorted(path.name for path in (PROJECT / "backend/src/main/resources/db/migration").glob("*.sql")),
    "documentMappingEntries": len(mapping["entries"]),
    "validationReportIncluded": (PROJECT / "VALIDATION-REPORT.md").exists(),
    "sha256": project_hashes,
}
(PROJECT / "DELIVERY-MANIFEST.json").write_text(json.dumps(project_manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

all_files = sorted(path for path in REPO.rglob("*") if included(path) and path.name != "MANIFEST.md")
aggregate = hashlib.sha256()
for path in all_files:
    relative = path.relative_to(REPO).as_posix()
    aggregate.update(relative.encode("utf-8")); aggregate.update(b"\0"); aggregate.update(hashlib.sha256(path.read_bytes()).digest())
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
> 当前清单排除 Git、构建产物、Terraform Provider 下载、测试缓存和 CI 临时日志。

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
- 路径与内容聚合 SHA-256：`{aggregate.hexdigest()}`

单文件工程哈希见 `mini-commerce/DELIVERY-MANIFEST.json`。由于清单不能稳定包含自身哈希，聚合值排除本文件自身；工程清单也排除自身。
''', encoding="utf-8")

status = "已由同提交 VALIDATION-REPORT.md 证明完整运行门禁通过" if (PROJECT / "VALIDATION-REPORT.md").exists() else "等待发布工作流运行完整门禁"
(PROJECT / "BUILD-VERIFICATION.md").write_text(f'''# 构建验证说明

- 当前状态：{status}。
- 工程文件：{project_manifest['fileCount']}；
- Java 主源码：{project_manifest['javaMainFiles']}；
- Java 测试：{project_manifest['javaTestFiles']}；
- Flyway Migration：{len(project_manifest['migrations'])}；
- 文档章节映射：{project_manifest['documentMappingEntries']}；
- MCP Python 源码与测试已通过语法编译检查。

完整命令、工具链和结论见 `VALIDATION-REPORT.md`。该报告不存在时，不得宣称 Maven、Testcontainers、Docker 或 Terraform 已通过。
''', encoding="utf-8")

print(json.dumps({"status": "delivery-finalized-v6", "counts": counts, "project": {k:v for k,v in project_manifest.items() if k != "sha256"}, "aggregateSha256": aggregate.hexdigest()}, ensure_ascii=False))
