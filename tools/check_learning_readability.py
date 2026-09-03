#!/usr/bin/env python3
"""检查学习工程是否具备可阅读性和中文解释。

这不是代码风格偏好检查，而是防止再次出现“一整个类压成几行”和“只有实现没有为什么”的交付事故。
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
MAIN_JAVA = REPO_ROOT / "mini-commerce/backend/src/main/java"
TEST_JAVA = REPO_ROOT / "mini-commerce/backend/src/test/java"
REPORT = REPO_ROOT / "mini-commerce/docs/generated/readability-audit.md"
CHINESE = re.compile(r"[\u4e00-\u9fff]")


def inspect(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    errors: list[str] = []

    if path.name != "package-info.java":
        if len(lines) <= 8 and len(text) > 300:
            errors.append(f"代码被压缩成 {len(lines)} 行，无法作为学习源码阅读")
        if "/src/main/" in path.as_posix():
            if "/**" not in text or not CHINESE.search(text):
                errors.append("主源码缺少中文类级职责说明")
            if "对应文档" not in text:
                errors.append("主源码缺少对应文档映射")

    for number, line in enumerate(lines, start=1):
        if "\t" in line:
            errors.append(f"第 {number} 行包含 Tab，缩进不统一")
        if line.rstrip() != line:
            errors.append(f"第 {number} 行存在行尾空格")

    return errors


def main() -> int:
    java_files = []
    for root in (MAIN_JAVA, TEST_JAVA):
        if root.exists():
            java_files.extend(sorted(root.rglob("*.java")))

    failures: dict[str, list[str]] = {}
    for path in java_files:
        errors = inspect(path)
        if errors:
            failures[path.relative_to(REPO_ROOT).as_posix()] = errors

    # 这些不是格式偏好，而是最容易被误写、最需要解释“为什么”的核心学习点。
    critical_requirements = {
        "mini-commerce/backend/src/main/java/com/example/minicommerce/cart/infrastructure/CartItemEntity.java": (
            "为什么有 {@code ux_cart_product} 唯一约束",
            "为什么不公开 {@code setQuantity}",
        ),
        "mini-commerce/backend/src/main/java/com/example/minicommerce/order/application/CreateOrderService.java": (
            "创建订单的主业务流程",
            "合并重复商品并校验数量",
            "事务本身不会自动防止库存超卖",
        ),
        "mini-commerce/backend/src/main/java/com/example/minicommerce/inventory/application/InventoryService.java": (
            "库存预留不能使用",
        ),
    }
    for relative, required_markers in critical_requirements.items():
        path = REPO_ROOT / relative
        if not path.exists():
            failures.setdefault(relative, []).append("关键学习文件不存在")
            continue
        text = path.read_text(encoding="utf-8")
        for marker in required_markers:
            if marker not in text:
                failures.setdefault(relative, []).append(
                    f"缺少关键解释：{marker}"
                )

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    report_lines = [
        "# 学习源码可读性审计",
        "",
        f"- Java 文件数：{len(java_files)}",
        f"- 不合格文件数：{len(failures)}",
        "- 检查项：格式、中文职责说明、对应文档、高风险方法解释、Tab 与行尾空格。",
        "",
    ]
    if failures:
        report_lines.extend(["## 不合格项", ""])
        for path, errors in failures.items():
            report_lines.append(f"### `{path}`")
            report_lines.extend(f"- {error}" for error in errors)
            report_lines.append("")
    else:
        report_lines.extend(
            [
                "## 结果",
                "",
                "通过。所有主 Java 文件均已格式化，并包含中文职责、原因和文档映射。",
                "",
            ]
        )

    REPORT.write_text("\n".join(report_lines), encoding="utf-8")
    if failures:
        print(
            f"readability audit failed: {len(failures)} files",
            file=sys.stderr,
        )
        for relative, errors in failures.items():
            print(relative, file=sys.stderr)
            for error in errors:
                print(f"- {error}", file=sys.stderr)
        return 1
    print(f"readability audit passed: {len(java_files)} files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
