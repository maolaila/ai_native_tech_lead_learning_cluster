"""一次性修正文档示例与监控契约；不改历史数据库迁移。"""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def replace(p,old,new):
    f=ROOT/p;t=f.read_text();assert old in t,(p,old);f.write_text(t.replace(old,new))
p='mini-commerce/backend/src/main/java/com/example/minicommerce/order/application/CreateOrderService.java'
replace(p,'import com.example.minicommerce.shared.error.BusinessException;', 'import com.example.minicommerce.shared.transaction.AfterCommitExecutor;\nimport com.example.minicommerce.shared.error.BusinessException;')
replace(p,'public class CreateOrderService {','''public class CreateOrderService {
    // 不使用 .created：Prometheus 客户端把它作为保留后缀，会在导出时删除。
    // 在监控页面查询 commerce_orders_creation_total；这个名字也由自动化测试检查。
    public static final String CREATION_METRIC = "commerce.orders.creation";
    private final AfterCommitExecutor afterCommit;''')
replace(p,'            MeterRegistry metrics) {','            MeterRegistry metrics,\n            AfterCommitExecutor afterCommit) {')
replace(p,'        this.metrics = metrics;','        this.metrics = metrics;\n        this.afterCommit = afterCommit;')
replace(p,'        metrics.counter("commerce.orders.created").increment();','''        // 提交成功以后才加一次，避免事务最后提交失败却把订单算作成功。
        // 提交后到回调前仍可能宕机，所以 Counter 只用于监控趋势，不是财务账本。
        afterCommit.run(() -> metrics.counter(CREATION_METRIC).increment());''')
p='mini-commerce/backend/src/test/java/com/example/minicommerce/InfrastructureReadinessTest.java'
f=ROOT/p;t=f.read_text();i=t.rfind('}');t=t[:i]+'''
    /** 使用真实 Prometheus 导出器，不能用 SimpleMeterRegistry 代替命名验证。 */
    @Test
    void orderCounterExportsTheNameUsedByTheRuntimeProbe() {
        try (var registry = new io.micrometer.prometheusmetrics.PrometheusMeterRegistry(
                io.micrometer.prometheusmetrics.PrometheusConfig.DEFAULT)) {
            registry.counter(com.example.minicommerce.order.application.CreateOrderService.CREATION_METRIC)
                    .increment();
            assertThat(registry.scrape()).contains("commerce_orders_creation_total 1.0");
        }
    }
'''+t[i:];f.write_text(t)
p='02_backend_spring/05_日志_配置与健康检查.md'
replace(p,'@Value("${app.payment.read-timeout:3s}")\nprivate Duration readTimeout;', '@Value("${example.read-timeout-ms:3000}")\nprivate long readTimeoutMillis;')
replace(p,'程序启动时，请 Spring 查找 `app.payment.read-timeout`，把结果放进 `readTimeout`；如果没找到，就使用默认值 3 秒。','程序启动时，请 Spring 查找 `example.read-timeout-ms`，把数字放进 `readTimeoutMillis`；没有配置就用 3000 毫秒（3 秒）。这个 example 键只是语法示例，不是本项目实际支付配置。')
replace(p,':3s         找不到时使用的默认值\nDuration    Java 中表示一段时间的类型', ':3000       找不到时使用的默认值，单位由这里约定为毫秒\nlong        Java 的整数类型')
replace(p,'`@Value` 适合少量、独立的配置。','需要时间对象时，可以再调用 `Duration.ofMillis(readTimeoutMillis)`。不要假设普通 `@Value` 会像 Spring Boot 配置绑定器一样把 `3s` 自动转为 Duration；本工程带单位的时长由下面的 `@ConfigurationProperties` 读取。\n\n`@Value` 适合少量、独立的配置。')
replace(p,'单独示例：','下面是省略 import 的独立语法示例，不是本仓库另一个配置类；它用 payment 前缀。实际工程使用上面的 AppProperties 和 app.payment 前缀：')
p='mini-commerce/docs/observability.md'
f=ROOT/p;f.write_text(f.read_text()+'''
## 先验证“监控真的收到数据”

在 mini-commerce 目录启动 app 和 observability，运行一次 `python3 scripts/smoke.py` 后，执行：

```bash
python3 scripts/check_observability.py
```

检查两层：后端确实导出了订单计数；Prometheus 也确实抓到了它，而不是仅仅网页能打开。
Java 中的名字是 `commerce.orders.creation`；Prometheus 查询名是 `commerce_orders_creation_total`。
名字末尾不要用 `.created`：新 Prometheus Java 客户端保留这个后缀，会将它删掉。
本项目为这个命名写了真实导出器测试，并在完整容器验收中查询实际结果。

计数在订单事务提交后增加；同键重试不重新增加。但程序重启会重置进程内计数，提交后立即宕机也可能漏记，所以它不是“数据库订单总数”。观察近期速率可查询：

```promql
sum(rate(commerce_orders_creation_total[5m]))
```

官方核对：[Micrometer 1.13 指标后缀迁移说明](https://github.com/micrometer-metrics/micrometer/wiki/1.13-Migration-Guide#invalid-meter-suffixes)。本页已给出当前工程需要的用法，不必现在离开仓库阅读。
''')
p='mini-commerce/docs/JAVA-SYNTAX-FOR-BACKEND-BEGINNERS.md';f=ROOT/p;t=f.read_text();pos=t.index('\n');t=t[:pos+1]+'''\n> 本页短代码用于解释语法，可能省略 import、参数和完整方法体；不要单独当成一个可启动工程。要运行真实业务，请回到对应源码和项目的 HTTP 请求集。\n'''+t[pos+1:];f.write_text(t)
print('Metrics and configuration examples corrected; runtime verification follows.')
