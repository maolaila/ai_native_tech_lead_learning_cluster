#!/usr/bin/env python3
"""根据 SUMMARY.md 重新生成 FULL_BOOK.md，并为当前仓库生成 MANIFEST.md。

为什么需要这个脚本：
- 分章文档更新后，旧的 FULL_BOOK.md 可能仍保留旧内容；
- 新增后端小白词典后，合并版也应包含它们；
- MANIFEST 中的文件数量和 SHA-256 应与当前仓库一致。

脚本输出不包含当前时间，因此相同输入会得到相同结果，适合 CI 自动检查和提交。
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from collections import defaultdict
from pathlib import Path
from urllib.parse import unquote

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
SUMMARY_PATH = REPO_ROOT / "SUMMARY.md"
FULL_BOOK_PATH = REPO_ROOT / "FULL_BOOK.md"
MANIFEST_PATH = REPO_ROOT / "MANIFEST.md"

SUMMARY_LINK = re.compile(r"(?<!!)\[[^\]]*]\(([^)]+)\)")
INLINE_LINK = re.compile(r"(?<!!)\[([^\]]*)]\(([^)]+)\)")
IMAGE_LINK = re.compile(r"!\[([^\]]*)]\(([^)]+)\)")
EXTERNAL_PREFIXES = (
    "http://",
    "https://",
    "mailto:",
    "tel:",
    "data:",
    "javascript:",
)
EXCLUDED_LINK_TARGETS = {"FULL_BOOK.md", "MANIFEST.md"}


def split_target_and_title(raw: str) -> tuple[str, str]:
    """拆分 Markdown 的链接路径与可选标题。"""
    value = raw.strip()
    if value.startswith("<") and ">" in value:
        end = value.index(">")
        return value[1:end], value[end + 1 :]
    parts = value.split(maxsplit=1)
    return parts[0], (" " + parts[1]) if len(parts) == 2 else ""


def summary_documents() -> list[Path]:
    """按 SUMMARY.md 中的出现顺序取得要合并的 Markdown 文件。"""
    documents: list[Path] = []
    seen: set[Path] = set()
    text = SUMMARY_PATH.read_text(encoding="utf-8")

    for raw_target in SUMMARY_LINK.findall(text):
        target, _ = split_target_and_title(raw_target)
        target = unquote(target).split("#", 1)[0].split("?", 1)[0]
        if not target.endswith(".md") or target in EXCLUDED_LINK_TARGETS:
            continue
        path = (REPO_ROOT / target).resolve()
        try:
            path.relative_to(REPO_ROOT)
        except ValueError:
            continue
        if path.exists() and path not in seen:
            seen.add(path)
            documents.append(path)

    if not documents:
        raise SystemExit("SUMMARY.md 中没有找到可合并的 Markdown 文件")
    return documents


def rewrite_one_target(source: Path, raw: str) -> str:
    """把分章文件中的相对链接改成相对于仓库根目录的链接。"""
    target, title = split_target_and_title(raw)
    decoded = unquote(target)

    if (
        not decoded
        or decoded.startswith("#")
        or decoded.startswith("/")
        or decoded.startswith(EXTERNAL_PREFIXES)
        or "${" in decoded
        or "{{" in decoded
    ):
        return raw

    path_part, separator, fragment = decoded.partition("#")
    query_part = ""
    if "?" in path_part:
        path_part, query = path_part.split("?", 1)
        query_part = "?" + query

    resolved = (source.parent / path_part).resolve()
    try:
        root_relative = resolved.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return raw

    rewritten = root_relative + query_part
    if separator:
        rewritten += "#" + fragment
    return rewritten + title


def rewrite_markdown_links(source: Path, text: str) -> str:
    """只在代码围栏外改写 Markdown 链接。"""
    output: list[str] = []
    in_fence = False

    for line in text.splitlines():
        stripped = line.lstrip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_fence = not in_fence
            output.append(line)
            continue

        if not in_fence:
            line = IMAGE_LINK.sub(
                lambda match: "!["
                + match.group(1)
                + "](" 
                + rewrite_one_target(source, match.group(2))
                + ")",
                line,
            )
            line = INLINE_LINK.sub(
                lambda match: "["
                + match.group(1)
                + "](" 
                + rewrite_one_target(source, match.group(2))
                + ")",
                line,
            )
        output.append(line)

    suffix = "\n" if text.endswith("\n") else ""
    return "\n".join(output) + suffix


def build_full_book() -> None:
    documents = summary_documents()
    sections = [
        "# AI-Native Tech Lead / Architect 学习手册——合并版",
        "",
        "> 本文件由 `tools/rebuild_full_book_and_manifest.py` 根据 `SUMMARY.md` 自动生成，便于全文搜索和连续阅读。",
        "> 实际学习仍建议按后端小白入口或模块导航完成代码、测试和故障实验。",
        "",
        f"> 共合并 {len(documents)} 个 Markdown 文件。分章文件更新后，CI 会同步刷新本文件。",
        "",
        "---",
        "",
    ]

    for document in documents:
        relative = document.relative_to(REPO_ROOT).as_posix()
        content = rewrite_markdown_links(
            document, document.read_text(encoding="utf-8", errors="replace")
        ).strip()
        sections.extend(
            [
                f"<!-- source: {relative} -->",
                "",
                f"## 文件：`{relative}`",
                "",
                content,
                "",
                "---",
                "",
            ]
        )

    FULL_BOOK_PATH.write_text("\n".join(sections).rstrip() + "\n", encoding="utf-8")
    print(f"FULL_BOOK.md generated from {len(documents)} documents")


def tracked_and_untracked_files() -> list[Path]:
    """取得应交付的仓库文件；忽略 Git 明确排除的构建产物。"""
    commands = (
        ["git", "ls-files", "-z"],
        ["git", "ls-files", "--others", "--exclude-standard", "-z"],
    )
    relative_names: set[str] = set()
    for command in commands:
        result = subprocess.run(
            command,
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
        )
        relative_names.update(
            item.decode("utf-8")
            for item in result.stdout.split(b"\0")
            if item
        )

    files = []
    for relative_name in sorted(relative_names):
        if relative_name == "MANIFEST.md":
            continue
        path = REPO_ROOT / relative_name
        if path.is_file():
            files.append(path)
    return files


def validate_json_and_yaml(files: list[Path]) -> tuple[list[str], list[str]]:
    json_errors: list[str] = []
    yaml_errors: list[str] = []

    for path in files:
        relative = path.relative_to(REPO_ROOT).as_posix()
        try:
            if path.suffix.lower() == ".json":
                json.loads(path.read_text(encoding="utf-8"))
            elif path.suffix.lower() in {".yml", ".yaml"}:
                list(yaml.safe_load_all(path.read_text(encoding="utf-8")))
        except Exception as exception:  # 报告文件和具体错误，不把校验失败藏起来。
            message = f"{relative}: {type(exception).__name__}: {exception}"
            if path.suffix.lower() == ".json":
                json_errors.append(message)
            else:
                yaml_errors.append(message)

    return json_errors, yaml_errors


def module_name(path: Path) -> str:
    relative = path.relative_to(REPO_ROOT)
    return relative.parts[0] if len(relative.parts) > 1 else "(root)"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_manifest() -> None:
    files = tracked_and_untracked_files()
    empty_files = [
        path.relative_to(REPO_ROOT).as_posix()
        for path in files
        if path.stat().st_size == 0
    ]
    markdown_files = [path for path in files if path.suffix.lower() == ".md"]
    markdown_lines = 0
    markdown_characters = 0
    module_stats: dict[str, dict[str, int]] = defaultdict(
        lambda: {"files": 0, "markdown_lines": 0, "markdown_characters": 0, "bytes": 0}
    )

    for path in files:
        key = module_name(path)
        size = path.stat().st_size
        module_stats[key]["files"] += 1
        module_stats[key]["bytes"] += size
        if path.suffix.lower() == ".md":
            text = path.read_text(encoding="utf-8", errors="replace")
            line_count = len(text.splitlines())
            character_count = len(text)
            markdown_lines += line_count
            markdown_characters += character_count
            module_stats[key]["markdown_lines"] += line_count
            module_stats[key]["markdown_characters"] += character_count

    json_errors, yaml_errors = validate_json_and_yaml(files)
    total_bytes = sum(path.stat().st_size for path in files)

    lines = [
        "# 文件清单与校验摘要",
        "",
        "> 本文件由 `tools/rebuild_full_book_and_manifest.py` 自动生成。",
        "> 统计基于 Git 已跟踪文件及未被 `.gitignore` 排除的新生成文件；不包含本 MANIFEST。",
        "",
        "## 总体统计",
        "",
        f"- 文件数：{len(files)}（不含本 MANIFEST）",
        f"- Markdown 文件数：{len(markdown_files)}",
        f"- Markdown 总行数：{markdown_lines:,}",
        f"- Markdown 总字符数：{markdown_characters:,}",
        f"- 目录内容大小：{total_bytes:,} bytes",
        "",
        "## 模块统计",
        "",
        "| 模块 | 文件 | Markdown 行数 | Markdown 字符 | 字节 |",
        "|---|---:|---:|---:|---:|",
    ]

    for key in sorted(module_stats, key=lambda item: (item != "(root)", item)):
        stat = module_stats[key]
        lines.append(
            f"| `{key}` | {stat['files']} | {stat['markdown_lines']:,} | "
            f"{stat['markdown_characters']:,} | {stat['bytes']:,} |"
        )

    lines.extend(
        [
            "",
            "## 自动校验",
            "",
            f"- 空文件：{len(empty_files)}",
            f"- JSON 解析错误：{len(json_errors)}",
            f"- YAML 解析错误：{len(yaml_errors)}",
            "- Markdown 相对链接与 Java 文档映射：见 `mini-commerce/docs/generated/learning-reference-audit.md`",
            "- Java 格式和中文学习注释：见 `mini-commerce/docs/generated/readability-audit.md`",
            "- 后端小白资料完整性：见 `mini-commerce/docs/generated/beginner-learning-audit.md`",
        ]
    )

    if empty_files:
        lines.extend(["", "### 空文件", ""])
        lines.extend(f"- `{item}`" for item in empty_files)
    if json_errors:
        lines.extend(["", "### JSON 解析错误", ""])
        lines.extend(f"- `{item}`" for item in json_errors)
    if yaml_errors:
        lines.extend(["", "### YAML 解析错误", ""])
        lines.extend(f"- `{item}`" for item in yaml_errors)

    lines.extend(["", "## SHA-256（不含本文件）", ""])
    for path in files:
        relative = path.relative_to(REPO_ROOT).as_posix()
        lines.append(f"- `{sha256(path)}`  `{relative}`")

    MANIFEST_PATH.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    print(f"MANIFEST.md generated for {len(files)} files")

    if json_errors or yaml_errors:
        raise SystemExit(
            f"manifest validation failed: json={len(json_errors)}, yaml={len(yaml_errors)}"
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="重新生成合并版学习手册和仓库文件清单"
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--full-book", action="store_true", help="只生成 FULL_BOOK.md")
    mode.add_argument("--manifest", action="store_true", help="只生成 MANIFEST.md")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.full_book:
        build_full_book()
        return
    if args.manifest:
        build_manifest()
        return
    build_full_book()
    build_manifest()


if __name__ == "__main__":
    main()
