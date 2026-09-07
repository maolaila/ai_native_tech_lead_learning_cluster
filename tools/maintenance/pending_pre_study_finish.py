"""一次性收尾修复：不改历史迁移，核对原文后修改；审查流水线执行后删除本脚本。"""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[2]

def replace(path, old, new):
    f = ROOT / path
    text = f.read_text(encoding="utf-8")
    if old not in text:
        raise ValueError(f"原文已变化，请人工核对：{path}: {old[:80]}")
    f.write_text(text.replace(old, new), encoding="utf-8")

p = 'mini-commerce/backend/src/test/java/com/example/minicommerce/InfrastructureReadinessTest.java'
replace(p, 'try (var registry =\n                new io.micrometer.prometheusmetrics.PrometheusMeterRegistry(\n                        io.micrometer.prometheusmetrics.PrometheusConfig.DEFAULT)) {', '''// 本版本 MeterRegistry 有 close()，但没有实现 AutoCloseable，不能放进 try(...)。
        var registry = new io.micrometer.prometheusmetrics.PrometheusMeterRegistry(
                io.micrometer.prometheusmetrics.PrometheusConfig.DEFAULT);
        try {''')
replace(p, 'assertThat(registry.scrape()).contains("commerce_orders_creation_total 1.0");\n        }', '''assertThat(registry.scrape()).contains("commerce_orders_creation_total 1.0");
        } finally {
            registry.close();
        }''')
p = 'mini-commerce/backend/src/main/resources/application.yml'
replace(p, 'management:\n  endpoints:', '''management:
  metrics:
    distribution:
      percentiles-histogram:
        # P95 图用的是直方图桶；不启用此项，图表公式存在但没有数据可算。
        http.server.requests: true
  endpoints:''')
p = 'mini-commerce/backend/src/test/java/com/example/minicommerce/BusinessSafetyIT.java'
f = ROOT / p
text = f.read_text(encoding='utf-8')
pos = text.rfind('}')
text = text[:pos] + '''
    @Autowired io.micrometer.core.instrument.MeterRegistry meters;
    @Autowired org.springframework.transaction.PlatformTransactionManager transactionManager;

    /** 只在真正提交后记一次；重复请求、回滚都不能多算订单。 */
    @Test
    void creationCounterReflectsCommitRatherThanMethodReturn() {
        var counter = meters.counter(CreateOrderService.CREATION_METRIC);
        double before = counter.count();
        create("metric-replay");
        create("metric-replay");
        assertThat(counter.count()).isEqualTo(before + 1);
        new org.springframework.transaction.support.TransactionTemplate(transactionManager)
                .executeWithoutResult(status -> {
                    create("metric-rollback");
                    status.setRollbackOnly();
                });
        assertThat(counter.count()).isEqualTo(before + 1);
        assertThat(jdbc.queryForObject(
                "select count(*) from idempotency_records where user_id=? and idempotency_key=?",
                Integer.class, buyer.id(), "metric-rollback")).isZero();
    }

    /** 仪表盘依赖这个配置，不能只验证仪表盘 JSON 合法。 */
    @Test
    void histogramRequiredByP95DashboardIsEnabled() {
        assertThat(environment.getProperty(
                "management.metrics.distribution.percentiles-histogram.http.server.requests"))
                .isEqualTo("true");
    }
''' + text[pos:]
f.write_text(text, encoding='utf-8')
p = 'mini-commerce/infra/observability/alerts.yml'
replace(p, 'clamp_min(sum(rate(http_server_requests_seconds_count[5m])), 1)', 'sum(rate(http_server_requests_seconds_count[5m]))')
replace(p, 'MiniCommerceOutboxBacklog', 'MiniCommerceOutboxPublishFailures')
p = 'mini-commerce/scripts/check_observability.py'
replace(p, '    # up=1 只证明抓取成功；还要查业务计数，避免网页可打开但业务指标为空。', '''    if not any(line.startswith("http_server_requests_seconds_bucket{") for line in text.splitlines()):
        raise AssertionError("后端没有 HTTP 直方图桶，Grafana 的 P95 图将没有数据")

    # up=1 只证明抓取成功；还要查业务计数，避免网页可打开但业务指标为空。''')
replace(p, '"backend-exporter",', '"backend-exporter",\n                        "http-histogram-buckets",')
p = 'mini-commerce/infra/observability/grafana/dashboards/mini-commerce.json'
f = ROOT / p
f.write_text(json.dumps(json.loads(f.read_text()), ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
p = 'mini-commerce/compose.yaml'
replace(p, 'name: mini-commerce', '''# 作用：把同一个商城需要的数据库、缓存、消息队列和应用一起启动。
# 为什么：容器之间使用下面的服务名连接；你的电脑访问的是 ports 左侧端口。
# 对应文档：08_runtime_deployment/02_Compose_Network_Volume_Health.md、mini-commerce/docs/LEARNING-READINESS.md。
# profiles 是可选分组：app 启动后端和 MCP，observability 启动监控。
# volumes 保存持久数据；down 不删数据，down -v 会删数据，学习时不要随手加 -v。
name: mini-commerce''')
p = 'mini-commerce/docs/LEARNING-READINESS.md'
f = ROOT / p
text = f.read_text(encoding='utf-8')
text += '''
## 10. 手动实验不要被占位符绊住

打开 [HTTP 请求集](../api/mini-commerce.http)，只执行第一组，先不要点“运行全部”。
带 `paste-` 的文字必须换成前一个请求实际返回的值；它不是系统中的默认数据。
首次下单示例不带优惠券，这样不会因为 Alice 的券已使用而卡住。优惠券计算另见本页第 4 节。

`200` 表示操作有正常响应，`201` 表示创建成功，`204` 表示成功但没有响应体。
`400` 先检查格式和参数，`401` 先重新登录，`403` 检查当前用户的权限，`409` 阅读响应中的 code 和 detail。
这些预期的业务拒绝不是服务器崩溃；不要直接把所有失败都改成返回 200。

第一次下单后请查看数据库，而不是只相信成功 JSON。在 mini-commerce 目录运行（默认数据库名/账号）：

```bash
docker compose exec postgres psql -U commerce_app -d commerce
```

进入后执行：

```sql
SELECT id, order_number, status, total_amount, currency
FROM orders ORDER BY created_at DESC LIMIT 5;
SELECT product_id, available, reserved FROM inventory ORDER BY product_id;
SELECT status, count(*) FROM outbox_events GROUP BY status;
```

输入 `\\q` 返回普通终端。上面都是查询语句，不会改数据。索引和锁实验晚些再做。
仓库根目录的 tools/scaffold 与历史 apply/finalize 脚本是早期制作材料，不是另一套要学习的商城；不要运行它们覆盖当前源码。
'''
f.write_text(text, encoding='utf-8')
p = 'mini-commerce/docs/observability.md'
f = ROOT / p
f.write_text(f.read_text(encoding='utf-8') + '''

### P95、Counter 和告警分别在说什么

P95 可以先理解为“这一段时间里，大约 95% 的请求比它快”。它不是平均值，直方图算出的值是估计值。
本项目已打开 `http.server.requests` 的直方图桶。先调用几个接口，等至少两次抓取后再看 Grafana；刚启动时空图不等于程序坏了。

Counter 是“从这次进程启动以来累计发生多少次”。看失败趋势通常用 rate/increase，不直接用累计值永久报警。
错误率等于失败请求速率除以全部请求速率，不能为了避免除零把分母随意改成 1。完全没有请求时，比例没有意义。
Outbox 发布失败告警不是“待发消息积压量”的监测；要监测积压，应另外统计未发布记录数及最老事件等待时间。
''', encoding='utf-8')
(ROOT / 'mini-commerce/api/mini-commerce.http').write_text('''# Mini Commerce 手动学习请求集：在 IDE 的 HTTP Client 中一次只执行一个 ### 请求。
# 对应文档：mini-commerce/docs/LEARNING-READINESS.md 第 2～5、10 节；
# mini-commerce/docs/REQUEST-TO-DATABASE-WALKTHROUGH.md；02_backend_spring/06_订单模块案例.md。
# 没有 HTTP Client 时，先运行 scripts/smoke.py；它使用同一组业务 API，不需要另学前端。
# 禁止“运行全部”：下单、支付、取消、退款都是修改数据的操作。
# 这里的密码仅供本地 local Profile；不要向生产环境发送这些请求。

@base = http://127.0.0.1:18080
# 源码方式启动后端时，改为 http://127.0.0.1:8080；不要改成数据库的端口。
@access = paste-accessToken-from-login
# 登录响应的 accessToken 完整复制到上一行。Bearer 是固定前缀，不是令牌的一部分。
@productId = paste-product-id-from-list
# 商品 ID 是数字；订单、支付 ID 是 UUID 字符串。它们不是同一个编号。
@orderId = paste-id-from-create-order
@paymentId = paste-paymentId-from-pay
# 同一次操作因为网络问题重试，要保留原 Key 和原请求内容。
# 想新增另一笔真实订单时，手动把下面的后缀一起改成新的值，例如 002。
@orderKey = study-order-001
@paymentKey = study-payment-001
@refundKey = study-refund-001

### A1. 登录 Alice：预期 200；复制 accessToken 到顶部 access
POST {{base}}/api/auth/login
Content-Type: application/json

{
  "email": "alice@example.com",
  "password": "Password123!"
}

### A2. 查询已上架商品：预期 200；从响应 content 数组复制一个商品的 id
# 新数据库有演示商品；不要假设 id 永远是 1。记住选中的名称、price、currency。
GET {{base}}/api/products?page=0&size=20

### A3. 放入购物车：quantity=1 表示“设为一件”，不是“再加一件”
PUT {{base}}/api/cart/items/{{productId}}
Authorization: Bearer {{access}}
Content-Type: application/json

{
  "quantity": 1
}

### A4. 查询自己的购物车：预期 200；购物车此时不会占用库存
GET {{base}}/api/cart
Authorization: Bearer {{access}}

### A5. 创建订单：预期 201；复制响应 id 到 orderId
# 请求只报商品和数量，不能提交自己计算的总价；第一次不使用优惠券。
# 这里显式提交 items，不是自动读取购物车。当前工程下单成功也不会自动清空购物车。
# 重复执行本请求（同 Key、同内容）应返回同一个订单 id，不能重复预留库存。
# 改了数量却继续使用原 Key，会返回 409 幂等冲突；这是预期保护，不是系统崩溃。
POST {{base}}/api/orders
Authorization: Bearer {{access}}
Idempotency-Key: {{orderKey}}
Content-Type: application/json

{
  "items": [
    {
      "productId": {{productId}},
      "quantity": 1
    }
  ]
}

### A6. 再查一次订单：预期 200，status=PENDING_PAYMENT
# 以真实查询结果和数据库为准，不只相信上一步创建接口的 JSON。
# 若此订单早就付过款，同 Key 重放返回的是旧订单；不是又生成了一笔待付订单。
GET {{base}}/api/orders/{{orderId}}
Authorization: Bearer {{access}}

### A7. 模拟支付：预期 200，status=SUCCEEDED；复制 paymentId 到顶部
# success 只是本地模拟器的控制词，不是真实支付凭证，不会扣你的钱。
# 同 Key 重试只读取原处理结果。学习 decline/unknown/timeout 时必须另建新订单。
POST {{base}}/api/payments/orders/{{orderId}}
Authorization: Bearer {{access}}
Idempotency-Key: {{paymentKey}}
Content-Type: application/json

{
  "paymentToken": "success"
}

### A8. 支付后重新查询订单：预期 status=PAID
GET {{base}}/api/orders/{{orderId}}
Authorization: Bearer {{access}}

### A9. 查询站内通知：预期 200；等待几秒再查，应出现与这笔订单有关的通知
# 通知由 RabbitMQ 的异步消费者写入，不保证支付响应返回的那一刻就已存在。
GET {{base}}/api/notifications
Authorization: Bearer {{access}}

# 第一组到这里结束。写三句话：哪一步查数据库，哪一步预留库存，哪一步发消息。
# 第二组是可选实验；不要为了“把文件都运行完”而继续操作。

### B1. 付款后、履约前的全额模拟退款：预期 200，status=SUCCEEDED
# 只对上面的已付款订单操作。重复同 Key 不会重复退款；不包含退货/部分退款/积分冲正。
POST {{base}}/api/payments/{{paymentId}}/refunds
Authorization: Bearer {{access}}
Idempotency-Key: {{refundKey}}

### B2. 退款后重新查询订单：预期 status=REFUNDED
GET {{base}}/api/orders/{{orderId}}
Authorization: Bearer {{access}}

### B3. 从购物车删除这件商品：预期 204，没有 JSON 响应体
# 这不会撤销已经生成的订单；订单与购物车是不同的业务记录。
# 再次删除可能返回 404，但“商品已经不在购物车”这个最终状态仍然相同。
DELETE {{base}}/api/cart/items/{{productId}}
Authorization: Bearer {{access}}

# C 组：取消实验。先把 orderKey 改成一个新值，再执行 A5，更新 orderId；不要执行 A7。
### C1. 取消未付款的新订单：预期 200，status=CANCELLED
# 不要对 PAID、REFUNDED 或支付 UNKNOWN 的订单执行并期待成功。
POST {{base}}/api/orders/{{orderId}}/cancellation
Authorization: Bearer {{access}}

### C2. 再查询：预期 CANCELLED；重复取消不能把库存归还两次
GET {{base}}/api/orders/{{orderId}}
Authorization: Bearer {{access}}

# 错误先看 HTTP 状态码及响应的 code/detail：
# 400：变量未替换、UUID 格式错、缺少头/字段；401：accessToken 未填写或过期；
# 403：当前身份无权；404：记录不存在；409：库存/状态/幂等冲突；
# 429：请求过快；503：依赖不可用或系统繁忙。不要通过删除校验来“修好”这些保护。
''', encoding='utf-8')
print('Reviewed fixes applied; compilation, PostgreSQL and full runtime acceptance are still required.')
