#!/usr/bin/env python3
"""扫描 Java 源码中的注解，生成适合初学者反查的使用位置索引。"""

from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
JAVA_ROOT = REPO_ROOT / "mini-commerce/backend/src"
MARKDOWN_OUTPUT = (
    REPO_ROOT / "mini-commerce/docs/generated/annotation-usage-index.md"
)
JSON_OUTPUT = REPO_ROOT / "mini-commerce/docs/generated/annotation-usage-index.json"

ANNOTATION_PATTERN = re.compile(r"(?<!\w)@([A-Z][A-Za-z0-9_]*)\b")


def scan() -> dict[str, list[dict[str, object]]]:
    usages: dict[str, list[dict[str, object]]] = defaultdict(list)
    for path in sorted(JAVA_ROOT.rglob("*.java")):
        relative = path.relative_to(REPO_ROOT).as_posix()
        text = path.read_text(encoding="utf-8")
        for line_number, line in enumerate(text.splitlines(), start=1):
            for match in ANNOTATION_PATTERN.finditer(line):
                usages[match.group(1)].append(
                    {
                        "path": relative,
                        "line": line_number,
                    }
                )
    return dict(sorted(usages.items()))


def markdown_link(relative_path: str) -> str:
    # 当前文件在 mini-commerce/docs/generated，回到 mini-commerce 需要 ../..
    project_relative = relative_path.removeprefix("mini-commerce/")
    return f"../../{project_relative}"


def render(usages: dict[str, list[dict[str, object]]]) -> str:
    lines = [
        "# Java 注解使用位置索引",
        "",
        "> 本文件由 `tools/generate_annotation_usage_index.py` 自动生成。",
        "> 注解作用的通俗解释见 [`SPRING-JAVA-ANNOTATIONS.md`](../SPRING-JAVA-ANNOTATIONS.md)。",
        "",
        f"- 注解种类：{len(usages)}",
        f"- 注解出现次数：{sum(len(items) for items in usages.values())}",
        "",
        "## 使用方法",
        "",
        "1. 先在注解词典中看它的通俗解释；",
        "2. 再从本页打开真实源码；",
        "3. 只观察它贴在类、方法、参数还是字段上；",
        "4. 思考去掉它后，程序会发生什么变化。",
        "",
    ]

    for annotation, items in usages.items():
        lines.extend([f"## `@{annotation}`", "", f"出现 {len(items)} 次。", ""])
        seen: set[str] = set()
        for item in items:
            path = str(item["path"])
            if path in seen:
                continue
            seen.add(path)
            line = int(item["line"])
            lines.append(
                f"- [`{path}`]({markdown_link(path)}#L{line})：首次出现在第 {line} 行"
            )
            if len(seen) >= 12:
                remaining = len({str(value["path"]) for value in items}) - len(seen)
                if remaining > 0:
                    lines.append(f"- 其余 {remaining} 个文件可在 IDE 中全局搜索 `@{annotation}`")
                break
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    usages = scan()
    MARKDOWN_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    MARKDOWN_OUTPUT.write_text(render(usages), encoding="utf-8")
    JSON_OUTPUT.write_text(
        json.dumps(usages, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(
        "generated annotation index:",
        len(usages),
        "types,",
        sum(len(items) for items in usages.values()),
        "usages",
    )


if __name__ == "__main__":
    main()
