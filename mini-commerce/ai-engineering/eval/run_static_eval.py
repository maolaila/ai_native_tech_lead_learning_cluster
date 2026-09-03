#!/usr/bin/env python3
"""对几条关键架构规则做快速、可重复的静态检查。

这些检查不能替代单元测试和集成测试，但能在几秒内发现非常明显的倒退，
例如请求 DTO 又允许客户端提交最终成交价，或者库存条件更新被误删。
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
JAVA_ROOT = PROJECT_ROOT / "backend/src/main/java"


def read(relative_path: str) -> str:
    return (PROJECT_ROOT / relative_path).read_text(encoding="utf-8")


def record_components(source: str, record_name: str) -> str:
    """取得 Java record 圆括号中的组件文本。

    不能简单搜索整个 OrderDtos.java，因为响应 DTO 合理地包含 totalAmount，
    真正需要禁止的是 CreateOrderRequest 接收客户端总价。
    """
    marker = f"record {record_name}"
    marker_index = source.find(marker)
    if marker_index < 0:
        raise ValueError(f"没有找到 record {record_name}")

    open_index = source.find("(", marker_index + len(marker))
    if open_index < 0:
        raise ValueError(f"record {record_name} 缺少组件列表")

    depth = 0
    for index in range(open_index, len(source)):
        character = source[index]
        if character == "(":
            depth += 1
        elif character == ")":
            depth -= 1
            if depth == 0:
                return source[open_index + 1 : index]

    raise ValueError(f"record {record_name} 的括号没有闭合")


def add_check(
    checks: list[dict[str, object]],
    name: str,
    condition: bool,
    evidence: str,
) -> None:
    checks.append(
        {
            "name": name,
            "passed": bool(condition),
            "evidence": evidence,
        }
    )


def main() -> int:
    checks: list[dict[str, object]] = []
    all_java = "\n".join(
        path.read_text(encoding="utf-8") for path in JAVA_ROOT.rglob("*.java")
    )

    order_dtos = read(
        "backend/src/main/java/com/example/minicommerce/order/api/OrderDtos.java"
    )
    create_order_components = record_components(order_dtos, "CreateOrderRequest")
    forbidden_client_price_fields = {
        "total",
        "totalAmount",
        "subtotal",
        "discount",
        "unitPrice",
        "price",
    }
    add_check(
        checks,
        "订单请求不接收客户端总价",
        not any(
            field_name in create_order_components
            for field_name in forbidden_client_price_fields
        ),
        "CreateOrderRequest 只包含商品、数量和优惠券；OrderResponse 可以正常返回 totalAmount",
    )

    normalized_java = "".join(all_java.split())
    add_check(
        checks,
        "条件库存更新",
        "available>=:qty" in normalized_java,
        "InventoryRepository.reserve 使用 WHERE available >= :qty",
    )

    baseline_sql = read("backend/src/main/resources/db/migration/V001__baseline.sql")
    add_check(
        checks,
        "Outbox 同工程存在",
        "outbox_events" in baseline_sql,
        "V001__baseline.sql 创建 outbox_events",
    )

    mcp_security = read("mcp-server/src/mini_commerce_mcp/security.py")
    add_check(
        checks,
        "MCP 拒绝 DDL",
        "write or DDL keyword" in mcp_security,
        "security.py 拒绝写 SQL 和 DDL 关键字",
    )

    passed = all(bool(check["passed"]) for check in checks)
    print(
        json.dumps(
            {
                "passed": passed,
                "checks": checks,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
