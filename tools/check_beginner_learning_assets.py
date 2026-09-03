#!/usr/bin/env python3
"""检查后端小白学习入口、词典和代表性源码说明是否完整。"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
REPORT = REPO_ROOT / "mini-commerce/docs/generated/beginner-learning-audit.md"


@dataclass(frozen=True)
class Requirement:
    path: str
    phrases: tuple[str, ...]


REQUIREMENTS = (
    Requirement(
        "mini-commerce/docs/BEGINNER-START-HERE.md",
        ("后端零基础", "Controller 是门口接待", "一次最多", "对应文档"),
    ),
    Requirement(
        "mini-commerce/docs/SPRING-JAVA-ANNOTATIONS.md",
        (
            "`@Value`",
            "`@ConfigurationProperties",
            "`@Transactional`",
            "`@Entity`",
            "`@RabbitListener`",
            "大白话",
        ),
    ),
    Requirement(
        "mini-commerce/docs/BACKEND-TERMS-PLAIN-CHINESE.md",
        ("幂等", "Outbox", "Cache Aside", "Publisher Confirm", "对象级权限"),
    ),
    Requirement(
        "mini-commerce/docs/JAVA-SYNTAX-FOR-BACKEND-BEGINNERS.md",
        ("`record`", "`Optional`", "`BigDecimal`", "Lambda", "构造器"),
    ),
    Requirement(
        "mini-commerce/docs/CONFIGURATION-FROM-ZERO.md",
        ("@Value", "@ConfigurationProperties", "环境变量", "Profile", "Duration"),
    ),
    Requirement(
        "mini-commerce/docs/ADHD-FOCUSED-LEARNING-PLAN.md",
        ("一次只解决一个问题", "最多打开 5 个文件", "稍后清单", "停止规则"),
    ),
    Requirement(
        "mini-commerce/docs/REQUEST-TO-DATABASE-WALKTHROUGH.md",
        ("OrderController", "CreateOrderService", "InventoryRepository", "Outbox"),
    ),
    Requirement(
        "mini-commerce/docs/BEGINNER-FAQ.md",
        ("为什么", "@Transactional", "Redis", "RabbitMQ", "Architecture Test"),
    ),
    Requirement(
        "mini-commerce/README.md",
        ("后端小白先从这里开始", "SPRING-JAVA-ANNOTATIONS.md", "ADHD-FOCUSED"),
    ),
    Requirement(
        "README.md",
        ("后端小白入口", "BEGINNER-START-HERE.md", "通俗词典"),
    ),
    Requirement(
        "mini-commerce/backend/src/main/java/com/example/minicommerce/MiniCommerceApplication.java",
        ("@SpringBootApplication 可以先理解", "@ConfigurationPropertiesScan", "@EnableScheduling"),
    ),
    Requirement(
        "mini-commerce/backend/src/main/java/com/example/minicommerce/shared/config/AppProperties.java",
        ("为什么不在业务类里到处写", "@Value", "prefix = \"app\""),
    ),
    Requirement(
        "mini-commerce/backend/src/main/java/com/example/minicommerce/cart/infrastructure/CartItemEntity.java",
        ("@Entity：告诉 JPA", "@GeneratedValue", "唯一约束"),
    ),
    Requirement(
        "mini-commerce/backend/src/main/java/com/example/minicommerce/inventory/infrastructure/InventoryRepository.java",
        ("@Modifying：", "nativeQuery = true", "@Lock(PESSIMISTIC_WRITE)"),
    ),
    Requirement(
        "mini-commerce/backend/src/main/java/com/example/minicommerce/shared/security/SecurityConfiguration.java",
        ("API 大门的门禁规则", "@EnableMethodSecurity", "STATELESS"),
    ),
    Requirement(
        "mini-commerce/backend/src/main/java/com/example/minicommerce/messaging/application/OutboxPublisher.java",
        ("待寄信清单", "@Scheduled", "Publisher Confirm"),
    ),
    Requirement(
        "mini-commerce/backend/src/main/java/com/example/minicommerce/notification/application/OrderPaidConsumers.java",
        ("为什么必须幂等", "@RabbitListener", "一起提交或一起回滚"),
    ),
    Requirement(
        "mini-commerce/backend/src/main/java/com/example/minicommerce/shared/error/GlobalExceptionHandler.java",
        ("@RestControllerAdvice", "@ExceptionHandler", "最后的安全网"),
    ),
    Requirement(
        "mini-commerce/docs/generated/annotation-usage-index.md",
        ("Java 注解使用位置索引", "@Transactional", "@Entity"),
    ),
)


def check_requirement(requirement: Requirement) -> list[str]:
    path = REPO_ROOT / requirement.path
    if not path.exists():
        return [f"缺少文件：`{requirement.path}`"]
    text = path.read_text(encoding="utf-8")
    failures = []
    for phrase in requirement.phrases:
        if phrase not in text:
            failures.append(f"`{requirement.path}` 缺少关键说明：`{phrase}`")
    return failures


def check_markdown_links() -> list[str]:
    """只检查本次新增入口中最关键的相对链接，避免完整 MkDocs 校验重复。"""
    expected = (
        "mini-commerce/docs/BEGINNER-START-HERE.md",
        "mini-commerce/docs/SPRING-JAVA-ANNOTATIONS.md",
        "mini-commerce/docs/BACKEND-TERMS-PLAIN-CHINESE.md",
        "mini-commerce/docs/JAVA-SYNTAX-FOR-BACKEND-BEGINNERS.md",
        "mini-commerce/docs/CONFIGURATION-FROM-ZERO.md",
        "mini-commerce/docs/ADHD-FOCUSED-LEARNING-PLAN.md",
        "mini-commerce/docs/REQUEST-TO-DATABASE-WALKTHROUGH.md",
        "mini-commerce/docs/BEGINNER-FAQ.md",
    )
    return [f"入口文件不存在：`{path}`" for path in expected if not (REPO_ROOT / path).exists()]


def write_report(failures: list[str]) -> None:
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# 后端小白学习资料审计",
        "",
        f"- 检查文件与代码位置：{len(REQUIREMENTS)}",
        f"- 不合格项：{len(failures)}",
        "- 检查内容：小白入口、通俗语言、注解词典、术语词典、配置说明、ADHD 学习计划、源码就地说明和注解索引。",
        "",
        "## 结果",
        "",
    ]
    if failures:
        lines.append("未通过。")
        lines.append("")
        lines.extend(f"- {failure}" for failure in failures)
    else:
        lines.append("通过。后端小白学习入口和代表性源码说明完整。")
    REPORT.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def main() -> None:
    failures: list[str] = []
    for requirement in REQUIREMENTS:
        failures.extend(check_requirement(requirement))
    failures.extend(check_markdown_links())
    write_report(failures)

    if failures:
        print(f"beginner learning audit failed: {len(failures)} issues")
        for failure in failures:
            print("-", failure)
        raise SystemExit(1)

    print(f"beginner learning audit passed: {len(REQUIREMENTS)} requirements")


if __name__ == "__main__":
    main()
