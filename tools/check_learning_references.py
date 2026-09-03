#!/usr/bin/env python3
"""检查 Markdown 相对链接和 Java 注释中的“对应文档”路径。

目标不是实现完整 Markdown 解析器，而是尽早发现学习入口点不开、
源码注释指向不存在章节等会直接打断学习的问题。
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import unquote

REPO_ROOT = Path(__file__).resolve().parents[1]
REPORT = REPO_ROOT / "mini-commerce/docs/generated/learning-reference-audit.md"

INLINE_LINK = re.compile(r"(?<!!)\[[^\]]*]\(([^)]+)\)")
IMAGE_LINK = re.compile(r"!\[[^\]]*]\(([^)]+)\)")
REFERENCE_LINK = re.compile(r"^\s*\[[^\]]+]:\s*(\S+)")
JAVA_DOC_PATH = re.compile(
    r"(?P<path>(?:mini-commerce/|(?:0[0-9]|1[0-6])_[A-Za-z0-9_\u4e00-\u9fff-]+/)"
    r"[A-Za-z0-9_./\u4e00-\u9fff-]+\.md)"
)

IGNORED_SCHEMES = (
    "http://",
    "https://",
    "mailto:",
    "tel:",
    "data:",
    "javascript:",
)


def clean_target(raw: str) -> str | None:
    """从 Markdown 链接中取出本地路径，去掉标题、查询参数和锚点。"""
    value = raw.strip()
    if value.startswith("<") and ">" in value:
        value = value[1 : value.index(">")]
    else:
        # [文本](path "title") 中只取 path。
        value = value.split(maxsplit=1)[0]

    value = unquote(value).strip()
    if not value or value.startswith("#") or value.startswith(IGNORED_SCHEMES):
        return None
    if "${" in value or "{{" in value:
        return None

    value = value.split("#", 1)[0].split("?", 1)[0]
    return value or None


def resolve_markdown_target(source: Path, target: str) -> Path | None:
    if target.startswith("/"):
        # 站点绝对路径依赖部署前缀，交给 MkDocs 严格构建检查。
        return None
    return (source.parent / target).resolve()


def markdown_failures() -> list[str]:
    failures: list[str] = []
    for path in sorted(REPO_ROOT.rglob("*.md")):
        if any(part in {".git", "site", "target", "node_modules"} for part in path.parts):
            continue

        in_fence = False
        for line_number, line in enumerate(
            path.read_text(encoding="utf-8", errors="replace").splitlines(),
            start=1,
        ):
            stripped = line.lstrip()
            if stripped.startswith("```") or stripped.startswith("~~~"):
                in_fence = not in_fence
                continue
            if in_fence:
                continue

            candidates = [
                *INLINE_LINK.findall(line),
                *IMAGE_LINK.findall(line),
            ]
            reference = REFERENCE_LINK.match(line)
            if reference:
                candidates.append(reference.group(1))

            for raw_target in candidates:
                target = clean_target(raw_target)
                if target is None:
                    continue
                resolved = resolve_markdown_target(path, target)
                if resolved is None:
                    continue
                try:
                    resolved.relative_to(REPO_ROOT)
                except ValueError:
                    failures.append(
                        f"`{path.relative_to(REPO_ROOT)}` 第 {line_number} 行链接越出仓库：`{target}`"
                    )
                    continue
                if not resolved.exists():
                    failures.append(
                        f"`{path.relative_to(REPO_ROOT)}` 第 {line_number} 行链接不存在：`{target}`"
                    )
    return failures


def java_mapping_failures() -> list[str]:
    failures: list[str] = []
    java_root = REPO_ROOT / "mini-commerce/backend/src"
    if not java_root.exists():
        return ["缺少 Java 源码目录：`mini-commerce/backend/src`"]

    for path in sorted(java_root.rglob("*.java")):
        text = path.read_text(encoding="utf-8", errors="replace")
        for match in JAVA_DOC_PATH.finditer(text):
            target = match.group("path")
            if not (REPO_ROOT / target).exists():
                failures.append(
                    f"`{path.relative_to(REPO_ROOT)}` 指向不存在的文档：`{target}`"
                )
    return failures


def write_report(failures: list[str]) -> None:
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# 学习资料内部引用审计",
        "",
        f"- 不合格项：{len(failures)}",
        "- 检查范围：Markdown 相对链接、Java 中文注释中的对应文档路径。",
        "",
        "## 结果",
        "",
    ]
    if failures:
        lines.append("未通过。")
        lines.append("")
        lines.extend(f"- {failure}" for failure in failures)
    else:
        lines.append("通过。学习入口和源码文档映射未发现失效本地路径。")
    REPORT.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def main() -> int:
    failures = markdown_failures() + java_mapping_failures()
    # 去重但保持稳定顺序，避免报告每次无意义变化。
    failures = list(dict.fromkeys(failures))
    write_report(failures)

    if failures:
        print(f"learning reference audit failed: {len(failures)} issues", file=sys.stderr)
        for failure in failures:
            print("-", failure, file=sys.stderr)
        return 1

    print("learning reference audit passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
