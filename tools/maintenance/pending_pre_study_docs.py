"""一次性、带旧内容断言的文档与注释修正；仅审计分支执行，完成后由工作流删除。"""
from pathlib import Path
import re
r = Path.cwd()
def edit(path, old, new):
    p=r/path; text=p.read_text(encoding='utf-8')
    assert old in text, (path, old)
    p.write_text(text.replace(old,new),encoding='utf-8')
def append(path,text):
    p=r/path;p.write_text(p.read_text(encoding='utf-8').rstrip()+'\n\n'+text.strip()+'\n',encoding='utf-8')
edit('mini-commerce/docs/BEGINNER-START-HERE.md',' domain/','domain/')
edit('mini-commerce/docs/BEGINNER-START-HERE.md','这个方法里的数据库修改要作为一个整体提交；中途出错时要一起回滚。','这个方法里的数据库修改作为一个整体提交；未捕获的运行时异常会触发默认回滚，受检异常需显式设置回滚规则。')
edit('mini-commerce/docs/CODE-READING-GUIDE.md','infra/compose.yaml','compose.yaml')
edit('mini-commerce/docs/CODE-READING-GUIDE.md','python tools/check_learning_readability.py','cd ../..  # 从 mini-commerce/backend 回到仓库根目录\npython tools/check_learning_readability.py')
f='mini-commerce/docs/REQUEST-TO-DATABASE-WALKTHROUGH.md'
edit(f,'示例：','以下是新建 local 演示数据库中 Alice 使用 WELCOME10 购买两件机械键盘的示例。先查询商品列表确认 ID；商品 ID 不保证永远是 1。该券只分配给 Alice，一旦占用或使用，不能换一个幂等键再次用它创建订单。')
edit(f,'中途失败时一起撤销。','未捕获的运行时异常触发默认回滚。受检异常需要 rollbackFor；主动吞掉异常不保证回滚。')
edit(f,'"number": "MC-20260903-AB12CD34"','"orderNumber": "示意订单号，以实际响应为准"')
edit(f,'"subtotal": 200.00,\n  "discount": 10.00,\n  "total": 190.00,\n  "currency": "CNY"','"subtotal": 16000.00,\n  "discount": 1000.00,\n  "totalAmount": 15000.00,\n  "currency": "JPY"')
edit(f,'示意：','以下只展示 OrderResponse 的部分字段。新演示商品单价 8000 JPY，购买两件小计 16000；10% 折扣受 1000 上限约束，因此实付 15000。完整响应还含 userId、items、createdAt。')
edit(f,'→ 等待 Publisher Confirm\n→ 标记为已发布','→ 等待 Publisher Confirm，并检查没有 mandatory Return（未路由退回）\n→ 用本次领取的 worker + attempt 凭证标记已发布')
edit(f,'Consumer 收到消息后可能：\n\n- 创建站内通知；\n- 记录积分；\n- 执行其他异步副作用。','创建订单的 `order.created.v1` 由 `OrderLifecycleConsumer` 记录审计，不会直接加积分或发付款通知。\n\n随后模拟付款成功，支付事务写入另一条 `order.paid.v1`；`OrderPaidConsumers` 的两个订阅才分别创建付款通知和积分。不要把“下单”和“付款成功”当成同一个事件。')
edit(f,'→ OrderPaidConsumers.java','→ OrderLifecycleConsumer.java\n\n付款后的另一条链：\nPaymentOrchestrator.java\n→ PaymentTransactionService.java\n→ OutboxPublisher.java\n→ OrderPaidConsumers.java')
append(f,'''## 十九、这次验收修复的一个重要陷阱

`@Modifying(clearAutomatically = true)` 不是“只刷新库存”。它会清空整个 JPA 持久化上下文，使已经加载的订单、支付和幂等记录都脱离自动跟踪。之后只修改这些对象的字段，未必会写入数据库。原来的实现因此出现“接口返回成功，数据库仍为 PROCESSING”。

本项目保留更新前的 flush，但不清空整个上下文；原生库存 SQL 更新后也不复用旧的库存实体。测试用 JDBC 重新查询数据库验证 COMPLETED/PAID，而不是只看返回的 Java 对象。

`flush` 是把已跟踪的修改送到数据库执行，**不是提交事务**；`clear` 是让 JPA 停止跟踪对象，**不是撤销 SQL**。详见[通俗术语词典](BACKEND-TERMS-PLAIN-CHINESE.md)。''')
f='mini-commerce/docs/SPRING-JAVA-ANNOTATIONS.md'
edit(f,'GET /api/orders/123','GET /api/orders/550e8400-e29b-41d4-a716-446655440000')
edit(f,'其中 `123` 会放进参数 `id`。','路径中的完整 UUID 字符串会转换成 UUID 对象。这里不能填 `123`：它不是合法 UUID，本项目会返回 400。')
edit(f,'@Value("${app.payment.read-timeout}")\nprivate Duration readTimeout;','@Value("${app.example.timeout-ms:3000}")\nprivate long timeoutMillis;')
edit(f,'程序启动时，请 Spring 找到 `app.payment.read-timeout`，然后把值放进 `readTimeout`。','程序启动时读取示例配置 app.example.timeout-ms；没有配置时使用 3000 毫秒。这是语法示例，不是本项目实际支付超时字段。')
edit(f,'@Value("${app.payment.read-timeout:3s}")','@Value("${app.example.timeout-ms:3000}")')
edit(f,'冒号后面的 `3s` 是默认值：','冒号后面的 `3000` 是默认值（单位由本示例约定为毫秒）：')
edit(f,'配置存在就用配置；配置不存在就暂时使用 3 秒。','配置存在就用配置；配置不存在就使用 3000 毫秒。Duration 的 3s 简写绑定由 Spring Boot 的 @ConfigurationProperties 支持，不要把所有 @Value 转换能力与它等同。')
append(f,'''## 验收补充：几个容易学错的标签

**`@Transactional(propagation = Propagation.MANDATORY)`：**调用者必须已经开启数据库事务；没有就报错。库存预留必须和订单在同一事务，不能单独提交。

**`@Transactional(rollbackFor = Exception.class)`：**本项目消息与回调处理还会抛出 JSON 解析等受检异常，因此显式要求它们回滚。默认规则是 RuntimeException 和 Error 回滚，而不是“任何异常都会回滚”。本项目采用默认代理模式，同一对象内部自调用不会经过事务代理；退款拆成 RefundService 与 RefundTransactionService 正是为了保证这一点。

**`@JdbcTypeCode(SqlTypes.CHAR)`：**Hibernate 扩展，明确告诉它数据库列是 CHAR。本项目币种列是 CHAR(3)，Java String 的默认 VARCHAR 映射并不等于 CHAR；真实数据库的 ddl-auto=validate 会核对映射。

**`@DirtiesContext`：**通知 Spring 测试框架丢弃旧的应用上下文。集成测试的每个测试类会重启 PostgreSQL 容器；不能把指向旧容器端口的连接池继续用于下一个类。这会增加测试启动时间，但避免错误复用。

**`@Modifying` 的 flush 与 clear：**flush 把已跟踪的修改发给数据库，事务尚可回滚；clear 使整个上下文里的对象脱离跟踪，不等于只刷新某条库存。现在的库存更新不再全局 clear。

参考：[Spring 事务注解规则](https://docs.spring.io/spring-framework/reference/data-access/transaction/declarative/annotations.html)、[Spring Data JPA 修改查询](https://docs.spring.io/spring-data/jpa/reference/jpa/query-methods.html)。''')
append('mini-commerce/docs/BACKEND-TERMS-PLAIN-CHINESE.md','''## 持久化上下文、托管对象、游离对象、flush 与 clear

把持久化上下文想成 JPA 的“正在跟踪的对象清单”。托管对象在清单里；事务提交时，JPA 会把检测到的字段变化写入数据库。游离对象不在清单里；继续给它赋值，只能确定 Java 内存改变了，不能确定数据库改变了。

`flush` 把跟踪到的修改发送给数据库执行，不等于 commit；当前事务仍可能回滚。`clear` 清空跟踪清单，不是回滚，也不是只刷新当前 Repository 的某个实体。原生 SQL 绕过对象跟踪，所以更新后内存里的旧库存对象可能过期。

本项目的验收测试特意不用测试方法自己的事务包住业务调用，并用 JDBC 重新读最终事实，避免出现“内存正确、数据库错误”的假通过。''')
edit('tools/check_learning_readability.py','通过。所有主 Java 文件均已格式化，并包含中文职责、原因和文档映射。','结构检查通过：已检查中文、文档路径和关键解释标记；格式以 Spotless 为准。本脚本不能证明注释语义正确或业务行为正确。')
edit('tools/check_learning_readability.py','- 检查项：格式、中文职责说明、对应文档、高风险方法解释、Tab 与行尾空格。','- 检查项：压缩行数、中文及文档路径标记、关键解释短语、Tab 与行尾空格；不是完整语义审查。')
edit('tools/check_beginner_learning_assets.py','通过。后端小白学习入口和代表性源码说明完整。','入口与关键短语检查通过；不等于全部资料准确、全部需求实现或运行验证通过。')
edit('mini-commerce/ai-engineering/eval/run_static_eval.py','    mcp_security = read("mcp-server/src/mini_commerce_mcp/security.py")\n    add_check(','''    # 执行拒绝逻辑，不用错误提示短语是否存在来冒充安全验证。
    sys.path.insert(0, str(PROJECT_ROOT / "mcp-server/src"))
    from mini_commerce_mcp.security import validate_readonly_sql
    rejected = 0
    for unsafe in ("drop table orders", "delete from orders", "EXPLAIN ANALYZE SELECT 1"):
        try:
            validate_readonly_sql(unsafe)
        except ValueError:
            rejected += 1
    add_check(''')
edit('mini-commerce/ai-engineering/eval/run_static_eval.py','"write or DDL keyword" in mcp_security','rejected == 3 and validate_readonly_sql("select 1") == "select 1"')
edit('tools/generate_complete_mini_commerce_v2.py','def generate() -> None:\n','def generate() -> None:\n    raise SystemExit("历史初始化生成器已停用，避免覆盖修复后的源码。学习和 CI 只能使用 --check；不要重新生成工程。")\n')
for p in (r/'.github/workflows').glob('*.yml'):
    if p.name not in {'beginner-learning-ci.yml','mini-commerce-ci.yml','pre-study-audit.yml'}:
        p.write_text('''name: Historical workflow (disabled)
on:
  workflow_dispatch:
permissions:
  contents: read
jobs:
  archived:
    runs-on: ubuntu-latest
    steps:
      - run: |
          echo '历史初始化/修复工作流已停用。当前学习源码已修正，不得重新生成或自动提升旧模板。'
          exit 1
''',encoding='utf-8')
for p in (r/'mini-commerce').glob('CI-FAILURE*.md'):
    p.write_text('> 历史故障记录，不代表当前版本状态。当前验收范围见 [正式学习说明](docs/LEARNING-READINESS.md)，运行结果以当前提交的 CI 为准。\n\n'+p.read_text(encoding='utf-8'),encoding='utf-8')
j=r/'mini-commerce/backend/src/main/java/com/example/minicommerce'
for p in j.rglob('*.java'):
    text=p.read_text(encoding='utf-8');name=p.stem
    if name.endswith('Dtos'):
        text=text.replace('负责路由、请求参数、校验、认证主体和 HTTP 响应转换，不承载核心业务规则。','定义请求允许传入的字段、字段校验和响应结构。DTO 是数据盒子，不处理路由、不查询数据库，也不会自己执行认证。')
    if name.endswith('Entity') and '负责 JPA、SQL、Redis、RabbitMQ 或外部系统等技术实现' in text:
        table=re.search(r'@Table\(\s*name\s*=\s*"([^"]+)"',text)
        table=table.group(1) if table else '对应'
        text=text.replace('负责 JPA、SQL、Redis、RabbitMQ 或外部系统等技术实现，并把技术细节隔离在业务边界之外。',f'把数据库 {table} 表的一条记录映射成 Java 对象，并保存本实体的状态。这个类不负责 Redis 或 RabbitMQ 通信。')
    if name.endswith('Repository'):
        text=text.replace('负责 JPA、SQL、Redis、RabbitMQ 或外部系统等技术实现，并把技术细节隔离在业务边界之外。','声明数据库查询或更新能力，由 Spring Data 创建实现；它不负责 Redis、RabbitMQ，也不决定整个业务流程。')
    p.write_text(text,encoding='utf-8')
p=j/'order/application/OrderQueryService.java';text=p.read_text(encoding='utf-8');idx=text.rfind('\n}')
text=text[:idx]+'''
    /** 能查看不等于能修改；客服可协助查询，但不可替别人取消订单。 */
    public void authorizeWrite(OrderEntity order, UserPrincipal actor) {
        if (!order.getUserId().equals(actor.id()) && !actor.role().name().equals("ADMIN")) {
            throw new BusinessException(ErrorCode.ACCESS_DENIED, "没有修改该订单的权限");
        }
    }
'''+text[idx:];p.write_text(text,encoding='utf-8')
edit('mini-commerce/backend/src/main/java/com/example/minicommerce/order/application/OrderCommandService.java','query.authorize(order, actor);','query.authorizeWrite(order, actor);')
edit('mini-commerce/backend/src/main/java/com/example/minicommerce/payment/application/PaymentTransactionService.java','query.authorize(order, actor);','''query.authorizeWrite(order, actor);
        if (!order.getUserId().equals(actor.id())) {
            throw new BusinessException(ErrorCode.ACCESS_DENIED, "只能为自己的订单创建支付");
        }''')
edit('mini-commerce/backend/src/main/java/com/example/minicommerce/order/api/OrderDtos.java','List<@Valid OrderLineRequest>','List<@NotNull @Valid OrderLineRequest>')
edit('mini-commerce/backend/src/main/java/com/example/minicommerce/order/api/OrderDtos.java','OrderLineRequest(@NotNull Long productId','OrderLineRequest(@NotNull @Positive Long productId')
edit('mini-commerce/backend/src/main/java/com/example/minicommerce/shared/config/AppProperties.java','支付相关配置。','支付相关配置。当前 FakePaymentGateway 不发 HTTP 请求；连接/读取超时是后续真实支付适配器的配置示例，并未自动作用于模拟器。')
edit('mini-commerce/mcp-server/Dockerfile','RUN useradd --system --uid 10001 app','RUN useradd --system --uid 10001 app && mkdir -p /audit && chown 10001:10001 /audit')
p=r/'mini-commerce/infra/k8s/backend.yaml';text=p.read_text(encoding='utf-8').replace('          ports:','          volumeMounts: [{name: temporary-files, mountPath: /tmp}]\n          ports:').replace('      terminationGracePeriodSeconds:','      volumes: [{name: temporary-files, emptyDir: {sizeLimit: 128Mi}}]\n      terminationGracePeriodSeconds:');p.write_text(text,encoding='utf-8')
for p in sorted(r.glob('[0-1][0-9]_*/README.md')):
    if p.parent.name in {'15_templates','16_references'}:continue
    text=p.read_text(encoding='utf-8');pos=text.find('\n')
    note='\n\n> 阅读定位：本模块同时包含原理、当前参考实现和后续练习。验收清单是你的学习目标，不表示这些能力都已在工程中完成；实际可运行范围见 [正式学习说明](../mini-commerce/docs/LEARNING-READINESS.md)。'
    p.write_text(text[:pos]+note+text[pos:],encoding='utf-8')
f='00_start/04_环境与版本基线.md'
edit(f,'当前稳定版本，示例避免依赖冷门 API','本工程锁定 3.5.7，以 backend/pom.xml 为准；不是要求安装最新版本')
edit(f,'Maven 或 Gradle；全项目选一种','Maven 3.9.x；本工程没有 Gradle 构建文件')
edit(f,'| Node | 当前 LTS |','| Node | 后续前端练习才需要；首次后端学习不需要 |')
edit(f,'18.x 学习环境','17，使用 compose.yaml 的 postgres:17-alpine')
edit(f,'| Redis | 当前稳定版本 |','| Redis | 8，使用 Compose 镜像 |')
edit(f,'当前稳定版本 + Management UI','4-management-alpine，使用 Compose 镜像')
edit(f,'| E2E | Playwright 当前稳定版本 |','| E2E | 后续前端练习使用 Playwright；本工程当前提供 HTTP Smoke |')
edit(f,'mvn -version       # 或 ./gradlew --version\nnode -v\nnpm -v','mvn -version       # 仅源码运行和 Java 测试需要\npython3 --version   # 文档站、Smoke 和 MCP 需要 Python 3.12/3.13')
edit(f,'```bash\ndocker compose up -d','```bash\ncd mini-commerce  # 从仓库根目录进入\ndocker compose up -d')
edit(f,'Java、构建工具、Node、Docker 正常','Docker 正常；源码模式再检查 Java/Maven；暂不安装 Node')
for rel in ['README.md','mini-commerce/README.md']:
    p=r/rel;text=p.read_text(encoding='utf-8').replace(' + 完整工程',' + 可运行教学工程').replace('Mini Commerce 完整学习工程','Mini Commerce 教学参考工程')
    text=text.replace('所有知识点都落在同一个电商业务','核心后端知识点围绕同一个电商业务').replace('Python MCP SDK 2.1.1、只读工具、沙箱、审计和 Eval','Python MCP SDK 2.1.1、只读工具、边界检查、审计和 Eval（不是完整沙箱）')
    text=text.replace('docker compose --profile app up -d --build','docker compose --profile app up -d --build --wait --wait-timeout 180').replace('cp .env.example .env','test -f .env || cp .env.example .env  # 不覆盖已有配置').replace('./scripts/smoke.sh','python3 scripts/smoke.py')
    text=text.replace('完整工程源码','教学参考工程源码').replace('均提供实际工程文件','提供对应文件；Kubernetes/AWS 是模板，不代表已在你的环境部署')
    p.write_text(text,encoding='utf-8')
append('README.md','''## 正式学习前的约定

先读 [正式学习说明与验收范围](mini-commerce/docs/LEARNING-READINESS.md)。当前没有前端成品、真实支付通道或已部署的云环境；本地默认密码只用于演示。原始路线、阶段门和练习不等于全部已实现功能。

现有环境更新前保留数据和 .env。旧演示库可能不满足新增支付唯一约束，不要随意删除业务记录或把 UNKNOWN 改成失败；初次学习可使用独立 Compose 项目，具体命令见正式学习说明。

文档站从 Git 跟踪的文件生成隔离快照，不复制 .env、临时日志或未跟踪文件。修改文档后重启预览；新增文档先 git add。''')
append('mini-commerce/README.md','''## 开始前先看当前范围

[正式学习说明](docs/LEARNING-READINESS.md) 是启动、端口、演示数据、更新旧数据库和未实现功能的统一入口。本文 Shell 命令在 mini-commerce 目录运行，Windows 使用 WSL2。Smoke 会创建专用演示账户、商品和模拟订单，不要对生产地址运行。

订单金额响应字段是 orderNumber、totalAmount；默认商品币种是 JPY。示例优惠券只分配给 Alice，不是所有新用户都有。退款只支持付款后、履约前的全额退款，暂不包含退货、库存返还和积分冲正。

MCP 的测试执行默认关闭，HTTP 模式不能开启；固定命令仍然会执行仓库代码，不应称为只读能力或完整沙箱。''')
p=r/'mini-commerce/backend/src/test/java/com/example/minicommerce/BusinessSafetyIT.java';text=p.read_text(encoding='utf-8');idx=text.rfind('\n}')
text=text[:idx]+'''
    @Test
    void supportCannotMutateAnotherPersonsOrder() {
        var order = create("support-order");
        var support = users.save(new UserEntity(UUID.randomUUID() + "@example.com", "support", "hash", UserRole.SUPPORT));
        var actor = UserPrincipal.from(support);
        assertThatThrownBy(() -> commands.cancel(order.id(), actor)).isInstanceOf(BusinessException.class);
        assertThatThrownBy(() -> paymentFlow.pay(order.id(), actor, "support-pay", "success")).isInstanceOf(BusinessException.class);
    }
'''+text[idx:];p.write_text(text,encoding='utf-8')
f='mini-commerce/docs/CONFIGURATION-FROM-ZERO.md';p=r/f;text=p.read_text(encoding='utf-8')
text=text.replace('不应该这样写：','需要随环境变化的值不宜在业务代码中这样写（固定的领域规则不一定需要配置）：')
text=text.replace('DB_HOST=postgres\nDB_PASSWORD=example','DATABASE_URL=jdbc:postgresql://localhost:15432/commerce\nDATABASE_USER=commerce_app\nDATABASE_PASSWORD=commerce-local')
text=text.replace('url: jdbc:postgresql://${DB_HOST:localhost}:5432/mini_commerce\n    password: ${DB_PASSWORD:postgres}','url: ${DATABASE_URL:jdbc:postgresql://localhost:15432/commerce}\n    username: ${DATABASE_USER:commerce_app}\n    password: ${DATABASE_PASSWORD:commerce-local}')
text=text.replace('${DB_HOST:localhost}','${DATABASE_PASSWORD:commerce-local}').replace('有 `DB_HOST` 就使用它；没有就使用 `localhost`。','有 DATABASE_PASSWORD 就使用它；没有就使用本地演示默认值 commerce-local。容器中的数据库地址由 compose.yaml 改为 postgres:5432，不是宿主机地址。')
text=text.replace('@Value("${app.payment.read-timeout}")\nprivate Duration readTimeout;','@Value("${app.example.timeout-ms:3000}")\nprivate long timeoutMillis;').replace('app.payment.read-timeout\n```\n\n是配置路径。','app.example.timeout-ms\n```\n\n是本段语法示例的配置路径；实际工程使用 AppProperties 的 Duration 字段。')
text=text.replace('@Value("${app.payment.read-timeout:3s}")','@Value("${app.example.timeout-ms:3000}")').replace('找不到配置 → 使用 3 秒','找不到配置 → 使用 3000 毫秒（本示例约定单位）')
text=text.replace('Spring 可以把文本配置转换成常见类型：','普通标量可以转换成 boolean、int、long。下面 Duration/DataSize 的单位简写专指 Spring Boot @ConfigurationProperties 绑定，不应推断任何 @Value 注入都有相同转换器：')
text=text.replace('SPRING_PROFILES_ACTIVE=local\n```','export SPRING_PROFILES_ACTIVE=local  # Bash/WSL，需 export 后子进程才能收到\nmvn -f backend/pom.xml spring-boot:run  # 当前目录 mini-commerce\n```').replace('java -jar app.jar --spring.profiles.active=local','mvn -f backend/pom.xml spring-boot:run -Dspring-boot.run.profiles=local')
text=text.replace('比：\n\n```yaml\nread-timeout: 5000','在绑定到 Duration 时比：\n\n```yaml\nread-timeout: 5000')
p.write_text(text,encoding='utf-8')
append(f,'''## 十九、实际运行中必须区分的配置

**不是所有超时属性都接受 5s。** 本项目 Hikari 的 connection-timeout/validation-timeout 对应毫秒 long，必须写 1500/1000，不是 1500ms/1000ms；AppProperties 的 Duration 则接受 500ms、2s。原先错误写法会使真实应用启动失败，已经由集成测试覆盖。

**有配置不等于实现使用了它。** FakePaymentGateway 不发 HTTP，所以 app.payment.connect-timeout/read-timeout 是真实支付适配器的预留示例；本次没有声称它们已控制模拟器的网络调用。

**test 只覆盖需要替换的属性。** application-test.yml 会继承主 application.yml；不再另放 src/test/resources/application.yml 影子文件。测试启用真实 Flyway 和 ddl-auto=validate，关闭消息监听与发布器；这与完整 Compose Smoke 的运行范围不同。

**默认配置不是生产就绪。** 目前没有给 AppProperties 全部字段建立完整的启动校验规则，没有自动的生产密钥合规检查。不要把“非 local 不创建默认账号”等同于“已经可以安全上线”。

完整端口、实际环境变量和从源码启动步骤见[正式学习说明](LEARNING-READINESS.md)。''')
# Generated book wording now matches read-only CI: regeneration is explicit, CI checks drift.
old='分章文件更新后，CI 会同步刷新本文件'
new='分章文件更新后，运行 tools/sync_learning_assets.py 同步刷新本文件；CI 校验结果'
edit('tools/rebuild_full_book_and_manifest.py',old,new)
edit('tools/check_beginner_learning_assets.py',old,new)
p=r/'tools/update_beginner_mkdocs_nav.py';text=p.read_text(encoding='utf-8')
text=text.replace('''    if '  - "后端小白专用入口":' in text:
        return False''','''    if '  - "后端小白专用入口":' in text:
        if "LEARNING-READINESS.md" not in text:
            text = text.replace('  - "后端小白专用入口":', '  - "后端小白专用入口":\\n      - "正式学习说明与验收范围": "mini-commerce/docs/LEARNING-READINESS.md"', 1)
            MKDOCS_PATH.write_text(text, encoding="utf-8")
            return True
        return False''')
text=text.replace('''    if "## 后端小白专用入口" in text:
        return False''','''    if "## 后端小白专用入口" in text:
        if "LEARNING-READINESS.md" not in text:
            text = text.replace("## 后端小白专用入口", "## 后端小白专用入口\\n\\n- [正式学习说明与验收范围](mini-commerce/docs/LEARNING-READINESS.md)", 1)
            SUMMARY_PATH.write_text(text, encoding="utf-8")
            return True
        return False''')
p.write_text(text,encoding='utf-8')
(r/'mini-commerce/BUILD-VERIFICATION.md').write_text('''# 构建验证状态该如何判断

文件数、Java 文件数和迁移列表见自动更新的 DELIVERY-MANIFEST.json；清单是来源完整性信息，不是测试结果。

以当前提交的 GitHub Actions 为准：mini-commerce-ci 运行 Java/Testcontainers、MCP 测试、真实 Compose HTTP Smoke 和 Terraform 静态校验；学习资料门禁运行格式、索引一致性、相对链接和严格模式文档构建。

[正式学习说明](docs/LEARNING-READINESS.md) 记录本次复现的问题、阶段性证据以及未验证范围。不得把跳过 Docker 的测试、静态分析或镜像构建成功表述成完整运行成功。
''',encoding='utf-8')
(r/'mini-commerce/docs/testing-strategy.md').write_text('''# 测试策略：每种证据能说明什么

| 检查 | 本项目的实际证据 | 不能据此声称 |
|---|---|---|
| 单元测试与架构测试 | 金额、订单状态、签名、缓存错误分支、Confirm/Return、分层依赖 | 所有业务流程已成功运行 |
| PostgreSQL 集成测试 | 真实 Flyway/Schema 校验、幂等与并发、支付/退款落库、权限、消费者去重、租约 | Redis 和 RabbitMQ 的网络交互已经被验证 |
| API 契约 | MockMvc 验证 400/401/403/405 等状态；测试不自行包裹事务 | 客户端连接或完整容器启动一定正常 |
| Compose Smoke | 真实容器、注册/登录、专用商品、下单与重放、支付、RabbitMQ 通知、退款 | 完整压测、全部故障组合、真实资金通道 |
| MCP 测试 | 路径与符号链接、拒绝 SQL、脱敏、注入标记、默认禁止执行 | 正则表达式是完整 SQL/提示注入安全证明 |
| Terraform validate | 配置结构与 Provider 约束 | 云资源已创建或网络/IAM 在真实账号可用 |
| 文档门禁 | 本地路径、标记、生成文件一致性、MkDocs 严格构建 | 每句文字都经过形式化验证 |

LearningReadinessIT 首先复现旧版本 7 个缺陷；测试断言数据库最终状态，不能只看 Java 返回对象。BusinessSafetyIT 扩展并发、重放、权限和消息状态验证。

Maven 的 test 运行单元/架构测试；verify 还运行名称为 *IT 的集成测试。CI 先要求 docker info 成功；本地无 Docker 时 Testcontainers 可能显示 skipped，**跳过不是通过**。

覆盖率只是执行痕迹。本仓库没有宣称达到固定覆盖率门槛，也没有完成 DLQ 全故障矩阵或生产压测。具体范围见[正式学习说明](LEARNING-READINESS.md)。
''',encoding='utf-8')
(r/'mini-commerce/docs/security.md').write_text('''# 安全边界与教学限制

API 使用 JWT，Refresh Token 只保存哈希并在轮换时加数据库行锁；BCrypt 密码限制按 UTF-8 字节检查，不把字符数当字节数。普通用户只能操作自己的订单；客服的协助查询不等于取消或付款权限，管理员也不能替别人的订单创建支付。

local 的默认账号、固定 JWT 密钥和 MCP Token 仅用于演示。没有自动生产合规检查；不应将本工程直接暴露公网。Compose 发布端口绑定 127.0.0.1；本地 Prometheus 可以读指标，其他管理端点仍要求管理员。

MCP 的数据库账号只有四张教学业务表的 SELECT，不能读取用户与 Token 表。文件检索先解析真实路径，禁止符号链接越界；脱敏按数据结构处理。白名单、超时和提示注入检测是有限防护，不是完整沙箱。

HTTP MCP 必须有 Bearer Token，测试执行默认关闭且 HTTP 不能开启。本地 stdio 显式开启测试执行后，仓库代码仍然有进程权限，必须先信任仓库。原生进程环境裁剪不代表容器级隔离。

Fake Webhook 的 HMAC 和事件 ID 去重只是教学实现；真实提供方还需要时间戳、防重放、密钥轮换和渠道契约核验。见[正式学习说明](LEARNING-READINESS.md)。
''',encoding='utf-8')
append('mini-commerce/docs/deployment.md','''## 模板不是已部署环境

Kubernetes 清单中的 replace 占位符、外部数据库和 Secret 需要自行配置；只读根文件系统为 /tmp 提供独立卷。AWS Terraform 只执行 fmt/init/validate，不执行 apply。发布、SLO 和回滚步骤是练习目标，不代表已有生产部署证据。旧数据库迁移和不删除旧数据的隔离启动方法见[正式学习说明](LEARNING-READINESS.md)。''')
append('mini-commerce/docs/observability.md','''## 实现边界

requestId 是本次入口关联号，traceId 由 Micrometer Tracing 管理，不能拿客户端的 X-Request-Id 覆盖。Outbox 里保存 traceId 并不自动建立跨消息的父子 Span。local 暴露 Prometheus 抓取端点且主机端口绑定本地；其他环境需要独立的管理网络和机器身份。Counter 不是业务数据库账本；失败告警看时间窗口内的增量，不用累计失败数大于零永久告警。''')
print('文档、注释、运行说明已修正；需要后续实际测试与容器验收。')
