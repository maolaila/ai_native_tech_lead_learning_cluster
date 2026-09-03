#!/usr/bin/env python3
"""为学习工程补齐中文职责说明和文档映射。

本脚本只补充“为什么”和“对应哪篇文档”，不会修改业务逻辑。
它与 Spotless 配合：先插入注释，再由 google-java-format 统一排版。
"""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
JAVA_ROOTS = (
    REPO_ROOT / "mini-commerce/backend/src/main/java",
    REPO_ROOT / "mini-commerce/backend/src/test/java",
)

MODULE_NAMES = {
    "audit": "审计",
    "cart": "购物车",
    "catalog": "商品目录",
    "identity": "身份与权限",
    "inventory": "库存",
    "messaging": "可靠消息",
    "notification": "通知",
    "observability": "可观测性",
    "order": "订单",
    "payment": "支付",
    "promotion": "优惠券",
    "shared": "共享技术基础",
}

MODULE_DOCS = {
    "audit": (
        "02_backend_spring/05_日志_配置与健康检查.md",
        "05_auth_security/02_RBAC与对象级权限.md",
        "10_observability/01_结构化日志与关联ID.md",
    ),
    "cart": (
        "00_start/02_长期项目_Mini_Commerce.md",
        "02_backend_spring/02_Controller_Service_Repository分层.md",
        "04_database_postgresql/01_关系模型_SQL与表关系.md",
    ),
    "catalog": (
        "02_backend_spring/03_DTO_Entity_Domain与映射.md",
        "06_redis/02_CacheAside_TTL与失效.md",
    ),
    "identity": (
        "05_auth_security/01_Session_Cookie_Token.md",
        "05_auth_security/02_RBAC与对象级权限.md",
        "05_auth_security/03_Web常见攻击.md",
    ),
    "inventory": (
        "04_database_postgresql/04_事务与Spring边界.md",
        "04_database_postgresql/05_并发_锁与库存超卖.md",
        "04_database_postgresql/06_隔离_MVCC与死锁.md",
    ),
    "messaging": (
        "07_rabbitmq/02_Exchange_Queue_Routing.md",
        "07_rabbitmq/03_Confirm_Ack_Retry_DLQ.md",
        "07_rabbitmq/04_幂等与Outbox.md",
    ),
    "notification": (
        "07_rabbitmq/01_同步异步与事件边界.md",
        "07_rabbitmq/04_幂等与Outbox.md",
    ),
    "observability": (
        "10_observability/01_结构化日志与关联ID.md",
        "10_observability/02_Metrics_RED_USE与百分位.md",
        "10_observability/03_Tracing与上下文传播.md",
    ),
    "order": (
        "02_backend_spring/06_订单模块案例.md",
        "04_database_postgresql/04_事务与Spring边界.md",
        "07_rabbitmq/04_幂等与Outbox.md",
    ),
    "payment": (
        "05_auth_security/03_Web常见攻击.md",
        "07_rabbitmq/04_幂等与Outbox.md",
        "11_system_design/04_韧性_Timeout_Retry_Circuit.md",
    ),
    "promotion": (
        "03_testing/02_测试用例设计.md",
        "04_database_postgresql/02_约束_范式与数据建模.md",
    ),
    "shared": (
        "02_backend_spring/01_请求生命周期与IoC_DI.md",
        "02_backend_spring/04_API设计_校验_异常与错误码.md",
        "11_system_design/02_模块化单体与边界.md",
    ),
}

LAYER_TEXT = {
    "api": (
        "HTTP/API 适配层",
        "负责路由、请求参数、校验、认证主体和 HTTP 响应转换，不承载核心业务规则。",
        "把 HTTP 细节留在系统边界，应用服务才能脱离 Web 框架测试和复用。",
    ),
    "application": (
        "应用用例编排层",
        "编排一个完整业务用例，协调领域规则、仓储、外部端口与事务边界。",
        "事务应该围绕业务动作，而不是分散在 Controller 或每个 Repository 中。",
    ),
    "domain": (
        "领域模型层",
        "表达业务状态、行为和不变量，并尽量保持对 Spring、HTTP 与数据库实现无感。",
        "领域方法比任意 Setter 更能阻止非法状态，也使测试直接描述业务语言。",
    ),
    "infrastructure": (
        "基础设施适配层",
        "负责 JPA、SQL、Redis、RabbitMQ 或外部系统等技术实现，并把技术细节隔离在业务边界之外。",
        "数据库表和框架会变化；隔离适配器可以避免这些变化扩散到业务规则和 API 契约。",
    ),
    "config": (
        "技术配置层",
        "集中声明 Bean、消息拓扑、安全链或基础设施参数。",
        "显式配置使运行时依赖、权限和失败边界可审查，也方便测试替换实现。",
    ),
    "security": (
        "安全边界层",
        "负责认证凭证解析、授权和安全策略，不把前端显示状态当成权限控制。",
        "安全必须在服务端默认拒绝，并通过角色、权限和对象所有权共同判断。",
    ),
    "test": (
        "自动化验证层",
        "提供可重复的行为、数据、并发或故障证据，而不是只证明代码能够编译。",
        "历史规则和 Bug 只有进入自动化测试，才不会在后续重构或 AI 生成代码时悄悄回归。",
    ),
}


def detect_module(path: Path) -> str:
    parts = path.parts
    if "minicommerce" in parts:
        index = parts.index("minicommerce")
        if index + 1 < len(parts):
            return parts[index + 1]
    return "shared"


def detect_layer(path: Path) -> str:
    if "/src/test/" in path.as_posix():
        return "test"
    for layer in ("api", "application", "domain", "infrastructure", "config", "security"):
        if layer in path.parts:
            return layer
    return "application"


def find_top_level_type(text: str) -> re.Match[str] | None:
    return re.search(
        r"\b(?:public\s+)?(?:abstract\s+|final\s+|sealed\s+|non-sealed\s+)?"
        r"(?:class|interface|enum|record)\s+(?P<name>[A-Za-z_$][A-Za-z0-9_$]*)",
        text,
    )


def class_javadoc(path: Path, class_name: str) -> str:
    module = detect_module(path)
    layer = detect_layer(path)
    module_name = MODULE_NAMES.get(module, module)
    title, purpose, rationale = LAYER_TEXT[layer]
    docs = MODULE_DOCS.get(module, MODULE_DOCS["shared"])
    docs_text = "、\n * ".join(f"{{@code {doc}}}" for doc in docs)
    return (
        "/**\n"
        f" * {module_name}模块的{title}：{{@code {class_name}}}。\n"
        " *\n"
        f" * <p><strong>作用：</strong>{purpose}</p>\n"
        f" * <p><strong>为什么：</strong>{rationale}</p>\n"
        " * <p><strong>对应文档：</strong>\n"
        f" * {docs_text}。</p>\n"
        " */\n"
    )


def add_class_javadoc(path: Path, text: str) -> tuple[str, bool]:
    if path.name == "package-info.java":
        return text, False

    declaration = find_top_level_type(text)
    if declaration is None:
        return text, False

    prefix = text[: declaration.start()]
    semicolon_positions = [match.end() for match in re.finditer(r";", prefix)]
    insert_at = semicolon_positions[-1] if semicolon_positions else 0

    between = text[insert_at : declaration.start()]
    if "对应文档：" in between:
        return text, False

    if "/**" in between and "*/" in between:
        module = detect_module(path)
        docs = MODULE_DOCS.get(module, MODULE_DOCS["shared"])
        docs_text = "、\n * ".join(f"{{@code {doc}}}" for doc in docs)
        mapping = (
            "\n *"
            "\n * <p><strong>对应文档：</strong>\n"
            f" * {docs_text}。</p>\n "
        )
        close_at = insert_at + between.rfind("*/")
        return text[:close_at] + mapping + text[close_at:], True

    comment = class_javadoc(path, declaration.group("name"))
    return text[:insert_at] + "\n\n" + comment + text[insert_at:].lstrip("\n"), True


def insert_before(text: str, literal: str, marker: str, comment: str) -> tuple[str, bool]:
    if marker in text or literal not in text:
        return text, False
    return text.replace(literal, comment + "\n" + literal, 1), True


def add_core_method_comments(path: Path, text: str) -> tuple[str, int]:
    """只给高风险业务方法补充原因注释，避免对 getter 等显然代码制造噪声。"""

    relative = path.relative_to(REPO_ROOT).as_posix()
    additions = 0

    rules: dict[str, list[tuple[str, str, str]]] = {
        "mini-commerce/backend/src/main/java/com/example/minicommerce/order/application/CreateOrderService.java": [
            (
                "@Transactional public OrderResponse create",
                "学习说明：创建订单事务边界",
                "/**\n"
                " * 学习说明：创建订单事务边界。\n"
                " *\n"
                " * <p>商品权威读取、服务端计价、库存预留、优惠券占用、订单快照、幂等结果和 Outbox\n"
                " * 必须同成同败，因此放在一个数据库事务中。外部支付不在这里调用，避免长事务和不可回滚副作用。</p>\n"
                " *\n"
                " * <p>对应文档：{@code 02_backend_spring/06_订单模块案例.md}、\n"
                " * {@code 04_database_postgresql/04_事务与Spring边界.md}、\n"
                " * {@code 07_rabbitmq/04_幂等与Outbox.md}。</p>\n"
                " */",
            ),
            (
                "private SortedMap<Long,Integer> normalize",
                "学习说明：先规范化订单项",
                "/**\n"
                " * 学习说明：先规范化订单项。\n"
                " *\n"
                " * <p>重复商品合并后再计算和扣减，避免一张订单出现多条相同商品；TreeMap 固定商品处理顺序，\n"
                " * 使多个并发订单以相同顺序触碰库存行，从而降低多商品死锁概率。</p>\n"
                " */",
            ),
        ],
        "mini-commerce/backend/src/main/java/com/example/minicommerce/inventory/application/InventoryService.java": [
            (
                "public void reserve(Map<Long,Integer> quantities)",
                "学习说明：库存预留不能先读后写",
                "/**\n"
                " * 学习说明：库存预留不能使用“查询库存→Java 中减法→保存”的普通读改写。\n"
                " *\n"
                " * <p>Repository 使用带条件的原子 UPDATE；受影响行数为 0 就表示库存不足。\n"
                " * 即使多个事务同时到达，数据库也只会让满足条件的更新成功。</p>\n"
                " */",
            ),
            (
                "public void release(Map<Long,Integer> quantities)",
                "学习说明：取消订单恢复预留",
                "/**\n"
                " * 学习说明：取消订单时把 reserved 数量恢复为 available。\n"
                " * 调用方必须先通过订单状态机保证取消只发生一次，并与订单状态修改处于同一事务。\n"
                " */",
            ),
            (
                "public void confirmSale(Map<Long,Integer> quantities)",
                "学习说明：支付成功确认销售",
                "/**\n"
                " * 学习说明：支付成功后只减少 reserved，不再减少 available，因为下单时已经完成预留。\n"
                " * 这样可以清楚区分“可售”“已预留”和“已成交”三个业务事实。\n"
                " */",
            ),
        ],
        "mini-commerce/backend/src/main/java/com/example/minicommerce/messaging/application/OutboxPublisher.java": [
            (
                "public void publishBatch()",
                "学习说明：Outbox 发布循环",
                "/**\n"
                " * 学习说明：Outbox 发布循环。\n"
                " *\n"
                " * <p>先从数据库领取待发布事件，再发送 RabbitMQ 并等待 Publisher Confirm；成功后标记已发布，\n"
                " * 失败则记录次数和下次重试时间。发布成功、标记前宕机仍可能重发，所以消费者仍必须幂等。</p>\n"
                " */",
            ),
        ],
        "mini-commerce/backend/src/main/java/com/example/minicommerce/messaging/application/ProcessedMessageService.java": [
            (
                "public boolean firstTime",
                "学习说明：消费者去重记录",
                "/**\n"
                " * 学习说明：消费者去重记录必须与业务副作用在同一事务中提交。\n"
                " * 如果先单独提交“已处理”再执行业务，业务失败后重试会被错误跳过。\n"
                " */",
            ),
        ],
    }

    for literal, marker, comment in rules.get(relative, []):
        text, added = insert_before(text, literal, marker, comment)
        additions += int(added)
    return text, additions


def main() -> None:
    changed_files = 0
    class_comments = 0
    method_comments = 0

    for root in JAVA_ROOTS:
        if not root.exists():
            continue
        for path in sorted(root.rglob("*.java")):
            original = path.read_text(encoding="utf-8")
            updated, class_added = add_class_javadoc(path, original)
            updated, method_added = add_core_method_comments(path, updated)
            if updated != original:
                path.write_text(updated, encoding="utf-8")
                changed_files += 1
            class_comments += int(class_added)
            method_comments += method_added

    report = REPO_ROOT / "mini-commerce/docs/generated/java-learning-comment-report.md"
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(
        "\n".join(
            [
                "# Java 中文学习注释生成报告",
                "",
                f"- 修改文件数：{changed_files}",
                f"- 新增类级职责/原因/文档映射：{class_comments}",
                f"- 新增高风险方法说明：{method_comments}",
                "",
                "说明：脚本只补充学习注释，不改变业务逻辑；随后由 Spotless 统一格式化。",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(
        f"annotated files={changed_files}, class_comments={class_comments}, "
        f"method_comments={method_comments}"
    )


if __name__ == "__main__":
    main()
