from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
PROJECT = REPO / "mini-commerce"


def write(relative: str, content: str) -> None:
    path = REPO / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


# 静态 Eval 只检查 CreateOrderRequest，不把服务端 Response 的 totalAmount 误判为客户端传价。
write("mini-commerce/ai-engineering/eval/run_static_eval.py", r'''from __future__ import annotations
import json
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[2]
checks = []

def check(name, condition, evidence):
    checks.append({"name": name, "passed": bool(condition), "evidence": evidence})

java = "\n".join(path.read_text(encoding="utf-8") for path in (root / "backend/src/main/java").rglob("*.java"))
order_dtos = (root / "backend/src/main/java/com/example/minicommerce/order/api/OrderDtos.java").read_text(encoding="utf-8")
request_block = order_dtos.split("public record CreateOrderRequest", 1)[1].split("public record OrderLineRequest", 1)[0]

check("创建订单请求不接收客户端总价", "totalAmount" not in request_block and "price" not in request_block,
      "OrderDtos.CreateOrderRequest")
check("库存使用数据库条件原子更新", "available>=:qty" in java, "InventoryRepository")
check("事务 Outbox 存在", "outbox_events" in (root / "backend/src/main/resources/db/migration/V001__baseline.sql").read_text(encoding="utf-8"), "V001")
check("支付跨幂等键有活跃支付唯一索引", "ux_payment_active_per_order" in (root / "backend/src/main/resources/db/migration/V001__baseline.sql").read_text(encoding="utf-8"), "V001")
check("同一支付只有一个全额退款聚合", "ux_refund_payment unique" in (root / "backend/src/main/resources/db/migration/V003__refunds.sql").read_text(encoding="utf-8"), "V003")
check("MCP 拒绝写 SQL", "write or DDL keyword" in (root / "mcp-server/src/mini_commerce_mcp/security.py").read_text(encoding="utf-8"), "security.py")
check("MCP 测试命令使用固定白名单", "SUITES=" in (root / "mcp-server/src/mini_commerce_mcp/tooling.py").read_text(encoding="utf-8"), "tooling.py")

result = {"passed": all(item["passed"] for item in checks), "checks": checks}
print(json.dumps(result, ensure_ascii=False, indent=2))
sys.exit(0 if result["passed"] else 1)
''')

# PostgreSQL varchar(40) 的测试订单号必须严格在列长度内。
test = PROJECT / "backend/src/test/java/com/example/minicommerce/order/OrderObjectAuthorizationIT.java"
text = test.read_text(encoding="utf-8")
text = text.replace('"AUTH-" + UUID.randomUUID()', '"AUTH-" + UUID.randomUUID().toString().substring(0, 12)')
test.write_text(text, encoding="utf-8")

# PostgreSQL 18 容器的官方数据布局使用 /var/lib/postgresql；Testcontainers 同步使用 18。
compose = PROJECT / "compose.yaml"
text = compose.read_text(encoding="utf-8")
text = text.replace("image: postgres:17-alpine", "image: postgres:18-alpine")
text = text.replace("postgres-data:/var/lib/postgresql/data", "postgres-data:/var/lib/postgresql")
# Nginx 以非 root 运行，所有临时文件放可写 tmpfs；不依赖 SETUID/SETGID capability。
text = text.replace('''    read_only: true
    tmpfs: [/var/cache/nginx, /var/run]
    security_opt: [no-new-privileges:true]
    cap_drop: [ALL]
    cap_add: [NET_BIND_SERVICE]
    networks: [commerce]

  mcp-server:''', '''    user: "101:101"
    read_only: true
    tmpfs: [/tmp]
    security_opt: [no-new-privileges:true]
    cap_drop: [ALL]
    networks: [commerce]

  mcp-server:''')
compose.write_text(text, encoding="utf-8")

abstract_it = PROJECT / "backend/src/test/java/com/example/minicommerce/support/AbstractPostgresIT.java"
abstract_it.write_text(abstract_it.read_text(encoding="utf-8").replace(
    'new PostgreSQLContainer<>("postgres:17-alpine")',
    'new PostgreSQLContainer<>("postgres:18-alpine")'), encoding="utf-8")

write("mini-commerce/infra/nginx/nginx.conf", r'''pid /tmp/nginx.pid;
events {}
http {
  client_body_temp_path /tmp/client_temp;
  proxy_temp_path /tmp/proxy_temp;
  fastcgi_temp_path /tmp/fastcgi_temp;
  uwsgi_temp_path /tmp/uwsgi_temp;
  scgi_temp_path /tmp/scgi_temp;

  log_format structured escape=json '{"time":"$time_iso8601","requestId":"$request_id","method":"$request_method","uri":"$uri","status":$status,"upstreamTime":"$upstream_response_time"}';
  access_log /dev/stdout structured;
  error_log /dev/stderr warn;

  upstream commerce_api { server backend:8080; keepalive 32; }
  server {
    listen 8088;
    client_max_body_size 2m;
    location / {
      proxy_pass http://commerce_api;
      proxy_http_version 1.1;
      proxy_set_header Connection "";
      proxy_set_header Host $host;
      proxy_set_header X-Forwarded-Proto $scheme;
      proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
      proxy_set_header X-Request-Id $request_id;
      proxy_connect_timeout 1s;
      proxy_read_timeout 5s;
      proxy_send_timeout 5s;
    }
  }
}
''')

# OpenAPI 中公开登录和商品读接口，其他接口继承 Bearer security。
openapi = PROJECT / "api/openapi.yaml"
text = openapi.read_text(encoding="utf-8")
text = text.replace("      operationId: login\n", "      operationId: login\n      security: []\n")
text = text.replace("      operationId: listProducts\n", "      operationId: listProducts\n      security: []\n")
openapi.write_text(text, encoding="utf-8")

write("mini-commerce/docs/document-review-and-corrections.md", r'''# 原学习文档审查与工程修订记录

本工程没有把原文档当作不可质疑的“答案”。原始纯文档快照保存在 `backup/docs-only-2026-09-03`；当前工程按照以下审查结论实现，并通过代码、数据库约束和测试补齐容易误读的部分。

## 已确认的主要问题与处理

### 1. `practice` 明确不是完整应用

原 `practice/README.md` 说明其只是最小实验材料。因此不能把几张 SQL 表和 Compose 当作最终工程。本仓库新增 `mini-commerce/`，实现身份、商品、库存、购物车、优惠券、订单、支付、退款、通知、积分、审计及生产工程链路。

### 2. 原实践 Schema 的订单状态缺少 `FULFILLING`

长期项目状态机包含 `FULFILLING`，但原实验 SQL 的 CHECK 列表没有。完整工程 Flyway `V001__baseline.sql` 统一包含该状态。原实验目录继续作为历史最小实验材料，不能作为应用 Schema Source of Truth。

### 3. “先查幂等键再保存”不能单独防并发

原订单伪代码用于解释边界，但若被直接照抄，两个并发请求可能都查不到记录。完整实现使用 PostgreSQL 事务级 advisory lock、数据库唯一约束、请求指纹和持久化结果；相同 Key 不同 Body 返回冲突。

### 4. `@Transactional` 不会自动防超卖

两个事务仍可能同时读到库存 1。工程使用 `UPDATE ... WHERE available >= quantity` 条件更新，并由 Testcontainers 并发测试证明 stock=1 时最多一个请求成功。

### 5. Outbox 不是“写一张表就完成”

工程补齐 `FOR UPDATE SKIP LOCKED`、领取租约、崩溃恢复、Publisher Confirm、Returned Message、退避重试、DLQ、`processed_messages` 和业务 Unique。Outbox 保证业务与待发送记录同事务，但消费者仍需幂等。

### 6. 外部支付/退款不能放在长数据库事务内

数据库无法回滚已发生的外部扣款。工程采用“短事务登记意图 → 事务外调用 → 短事务落结果”，并对响应丢失保留 `UNKNOWN`，不武断宣布失败。

### 7. 单个 API 幂等不等于跨 Key 不重复

不同幂等键仍可能同时对一个订单发起两次支付。工程增加订单级活跃支付唯一索引和行锁校验；全额退款也限定每个成功支付只有一个退款聚合。

### 8. 读权限不能复用于写权限

SUPPORT 可以按职责读取订单，不代表可以替用户支付或取消。工程将 `authorizeRead`、`authorizeOwner`、`authorizeOwnerOrAdmin` 分开，并提供 HTTP 对象级越权测试。

### 9. 版本“当前稳定”不可直接作为可重复构建基线

文档原理允许版本演进，但可执行工程必须锁定。当前工程锁定 Java 21、Spring Boot 3.5.7、MCP Python SDK 2.1.1、容器标签和 Terraform Provider 范围；升级必须重新运行全部门禁。版本本身不是永恒真理，锁文件和成功 CI 才是本次构建证据。

### 10. PostgreSQL 18 官方容器数据目录变化

完整工程使用 PostgreSQL 18，并将 Volume 挂载到 `/var/lib/postgresql`，避免沿用旧主版本的 `/var/lib/postgresql/data` 假设。AWS Terraform 暂用 RDS PostgreSQL 17 作为更保守的区域可用基线，两者均使用兼容 SQL，云上实际版本需在目标区域重新验证。

### 11. MCP SDK 2.x 存在破坏性变更

工程使用 `MCPServer` 和 2.1.1 的 Streamable HTTP 运行方式，不再使用旧版 `FastMCP` 导入。HTTP 模式使用 Bearer Token；stdio 本身没有 Authorization Header，其安全边界是启动它的本地进程。

### 12. 根 `MANIFEST.md` 在加入工程后必须重建

原清单只代表纯文档快照。发布脚本会生成“文档 + 工程”联合清单，原哈希保留在备份分支，避免把旧文件数和旧哈希继续当成当前事实。

## 没有声称解决的范围

该工程不是支付宝、淘宝或大型多地域生产系统；不声称替代正式 PCI、合规审计、灾备演练和云成本评审。它提供的是一套完整、可运行、可测试、可故障注入并能解释取舍的学习基线。
''')

write("mini-commerce/docs/code-reading-guide.md", r'''# 完整工程代码阅读顺序

不要按文件夹机械从上到下读。先沿一个订单的业务时间线阅读，再回到各技术模块。

## 第一遍：一条成功订单

1. `identity/api/AuthController` 与 `identity/application/AuthService`：身份怎样建立；
2. `catalog/api/ProductController`：HTTP 与 Application 分层；
3. `cart/application/CartService`：临时业务状态；
4. `order/application/CreateOrderService`：权威计价、优惠券、库存、快照、幂等、Outbox 的同一事务；
5. `inventory/infrastructure/InventoryRepository`：条件原子更新；
6. `order/infrastructure/OrderEntity`：状态机；
7. `payment/application/PaymentOrchestrator`：外部调用为何在事务外；
8. `messaging/application/OutboxPublisher`：至少一次发布；
9. `notification/application/OrderPaidConsumers`：幂等消费。

## 第二遍：失败、重复和并发

按 `labs/failure-matrix.md` 逐项制造：库存竞争、相同幂等键、不同幂等键支付、响应丢失、Redis/RabbitMQ 停机、毒消息、代理 502。每次同时观察 HTTP、数据库、Redis、Queue、日志、指标和 Trace。

## 第三遍：工程治理

阅读：

- `backend/src/test`：正确性的自动证据；
- `infra/observability`：上线后怎样看见；
- `.github/workflows/mini-commerce-ci.yml` 与 `Jenkinsfile`：门禁；
- `infra/aws/terraform`：本地组件如何映射到云；
- `ai-engineering/rules`、`golden-paths`、`eval`：经验怎样成为可执行体系；
- `mcp-server`：如何给 Agent 提供受控上下文和工具。

## 从文档跳代码

打开 `docs/generated/document-code-map.md`，按 Source ID、原文件和标题定位。代码注释中的文档路径解释局部设计原因；映射表覆盖整个文档章节空间。
''')

root_readme = REPO / "README.md"
text = root_readme.read_text(encoding="utf-8")
needle = "- [完整工程说明](mini-commerce/README.md)\n"
replacement = needle + "- [原文档审查与工程修订](mini-commerce/docs/document-review-and-corrections.md)\n- [完整工程代码阅读指南](mini-commerce/docs/code-reading-guide.md)\n"
if needle in text:
    text = text.replace(needle, replacement)
root_readme.write_text(text, encoding="utf-8")

project_readme = PROJECT / "README.md"
text = project_readme.read_text(encoding="utf-8")
needle = "完整章节映射见 `docs/generated/document-code-map.md`。"
replacement = "阅读前先看 `docs/document-review-and-corrections.md` 与 `docs/code-reading-guide.md`。\n\n" + needle
project_readme.write_text(text.replace(needle, replacement), encoding="utf-8")

print(json.dumps({"status": "ci-and-doc-fixes-v5-applied"}, ensure_ascii=False))
