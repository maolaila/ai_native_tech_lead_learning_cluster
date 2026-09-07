#!/usr/bin/env python3
"""只同步索引、合并书和校验清单；绝不重新生成或覆盖业务源码。"""
from __future__ import annotations
import hashlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(script: str, *args: str) -> None:
    subprocess.run([sys.executable, str(ROOT / script), *args], cwd=ROOT, check=True)


def main() -> None:
    run("tools/update_beginner_mkdocs_nav.py")
    # 只调用旧工具的读取文档生成索引函数，绝不调用 generate()。
    sys.path.insert(0, str(ROOT / "tools"))
    spec = importlib.util.spec_from_file_location("mapping_builder", ROOT / "tools/generate_complete_mini_commerce_v2.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.generate_mapping()
    folder = ROOT / "mini-commerce/docs/generated"
    mapping_path = folder / "document-code-map.json"
    mapping = json.loads(mapping_path.read_text(encoding="utf-8"))
    mapping.pop("generatedAt", None)
    mapping["scope"] = "suggested reading targets, not proof that every chapter requirement is implemented"
    mapping_path.write_text(json.dumps(mapping, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    note_path = folder / "document-code-map.md"
    note_path.write_text(note_path.read_text(encoding="utf-8").replace(
        "代码目标是同一业务工程中的实现位置，不是按章节复制 Demo。",
        "代码目标是建议阅读的相关位置，不表示该章节的全部验收目标已实现。"), encoding="utf-8")
    for item in mapping["entries"]:
        if not (ROOT / item["source"]).is_file(): raise ValueError(f"来源不存在：{item['source']}")
        for target in item["codeTargets"]:
            if not (ROOT / target).exists(): raise ValueError(f"代码目标不存在：{target}")
    run("tools/generate_annotation_usage_index.py")
    run("tools/rebuild_full_book_and_manifest.py", "--full-book")
    run("tools/check_learning_readability.py")
    run("tools/check_beginner_learning_assets.py")
    run("tools/check_learning_references.py")
    project = ROOT / "mini-commerce"
    tracked = subprocess.check_output(["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"], cwd=ROOT).decode("utf-8").split("\0")
    files = sorted({ROOT / name for name in tracked if name.startswith("mini-commerce/")
        and (ROOT / name).is_file() and not name.endswith("DELIVERY-MANIFEST.json")})
    manifest = {"scope": "source inventory, not test results", "fileCount": len(files),
        "javaMainFiles": len(list((project / "backend/src/main/java").rglob("*.java"))),
        "javaTestFiles": len(list((project / "backend/src/test/java").rglob("*.java"))),
        "migrations": sorted(p.name for p in (project / "backend/src/main/resources/db/migration").glob("V*.sql")),
        "sha256": {p.relative_to(project).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in files}}
    (project / "DELIVERY-MANIFEST.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    run("tools/rebuild_full_book_and_manifest.py", "--manifest")


if __name__ == "__main__": main()
