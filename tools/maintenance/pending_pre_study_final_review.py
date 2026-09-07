"""一次性执行已经审阅的文字修订和回归测试补充；执行后由审查工作流删除。"""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
JAVA = ROOT / 'mini-commerce/backend/src/main/java/com/example/minicommerce'
DOCS = ROOT / 'mini-commerce/docs'
# 每项针对具体类说明，保留原来的文档引用，不重新生成业务源码。
comments = {
 'RefreshTokenRepository': ('查找用于换取新登录凭证的刷新令牌记录。', '按 tokenHash 查找时加数据库写锁，让两个同时刷新同一令牌的请求排队；第一个撤销旧令牌后，第二个就不能再次使用它。'),
 'UserRepository': ('按邮箱或用户 ID 查找账户，注册时检查邮箱是否已经使用。', 'IgnoreCase 表示忽略邮箱大小写；真正防止并发重复注册还靠数据库 lower(email) 唯一索引，不只靠先查询。'),
 'RefreshTokenEntity': ('保存刷新令牌的哈希、归属用户、到期时间和撤销时间。', '数据库不保存可直接使用的原令牌；isValidAt 同时检查过期和撤销，不能只判断字符串是否存在。'),
 'AuthDtos': ('登录、注册、刷新和登出的请求与响应数据盒子。', 'RegisterRequest 不允许用户传入 ADMIN 角色；TokenResponse 也不返回密码哈希。校验注解描述输入规则，不会自行登录用户。'),
 'UserRole': ('账户可以选择的角色：普通用户、管理员和客服。', '角色不是某笔订单的所有权；客服能查单不等于能替用户付款，具体动作仍由服务端检查。'),
 'NotificationRepository': ('从 notifications 表分页读取某个用户的站内通知。', '按 userId 过滤要在数据库查询中完成，不能先返回所有人的消息再让客户端隐藏。'),
 'NotificationEntity': ('保存一条发给某个用户的站内通知，包括内容、未读标志和创建时间。', '这里的通知是一条数据库记录，不是已经发送的短信或邮件；当前项目没有实现短信发送或标记已读接口。'),
 'PointsLedgerEntity': ('保存一笔订单付款后增加的积分明细。', 'orderId 与 reason 的组合只能出现一次，作为重复消费的第二道防线。points 使用 long；当前退款流程还没有冲回积分。'),
 'PointsLedgerRepository': ('保存付款后产生的积分流水。', '这里继承 JpaRepository 的 save 等方法，不必手写相同的插入 SQL；积分计算仍由消费者负责。'),
 'ProductRepository': ('按商品 ID、SKU 和上架状态查询 products 表。', '展示查询和下单查询都需要过滤可售状态；下单直接使用本接口的数据库结果，不能把展示缓存当作成交依据。'),
 'ProductEntity': ('保存商品的名称、SKU、价格、币种和上下架状态。', '这是商品的当前信息，历史成交信息另存在 OrderItemEntity。version 帮助发现并发更新；不会自动代替库存扣减规则。'),
 'ProductDtos': ('规定创建商品、修改商品和返回商品时包含哪些字段。', '价格是 BigDecimal，限制小数位以匹配数据库；initialStock 是初始可售数量，不是已经卖出的数量。'),
 'ProductController': ('商品 HTTP 入口：公开查询商品，管理员创建、修改和上架商品。', '这里只把请求交给 ProductService，不直接修改库存或数据库；公开查看与管理员修改的权限不同。'),
 'ProductCacheInvalidationConsumer': ('收到商品变更事件后，删除对应商品的 Redis 展示缓存。', '下一次查询再加载数据库新值。重复删同一个缓存键无害，但删除失败不能声称已经获得强一致性。'),
 'ProductService': ('处理商品浏览、创建、修改和上架，并为下单提供数据库查询。', '创建商品同时初始化库存；修改后在事务提交后删缓存，并写入变更事件。authoritativeSellable 故意绕开展示缓存。'),
 'ProductStatus': ('商品的三个状态：草稿、已上架、已归档。', '只有 PUBLISHED 商品允许公开销售；枚举只限制选项，能否改变状态仍要看 ProductEntity 的方法。'),
 'JwtAuthenticationFilter': ('从 Authorization 请求头读取 Bearer Token，验证后找出当前用户。', '认证回答“你是谁”，不在这里决定“你能否看别人的订单”。每次还读取数据库中的启用状态和角色，不能只信旧 Token 的角色。'),
 'UserPrincipal': ('把已确认的用户 ID、邮箱和角色交给 Spring Security。', '它是当前请求的身份说明，不是数据库实体。getAuthorities 把角色转换成权限系统使用的 ROLE_ 前缀格式。'),
 'UserCouponRepository': ('查找发给某个用户的某张优惠券，并可锁住这条领券记录。', '优惠券模板和个人领取记录不同；锁住个人记录，是为了避免两张订单同时占用同一张券。'),
 'CouponEntity': ('保存优惠券模板：券码、折扣方式、最低消费、封顶金额和有效期。', '一张模板可发给不同用户；哪个用户已经占用或使用，由 UserCouponEntity 记录。'),
 'UserCouponEntity': ('保存某个用户领到的券，以及它被哪张订单占用。', 'reserve、markUsed、release 分别表示占用、用掉、退回。检查订单 ID，避免订单 A 释放订单 B 的券。'),
 'CouponRepository': ('按券码查找优惠券模板。', '模板查到并不代表当前用户有资格使用，还要查询个人领券记录并检查有效期和金额门槛。'),
 'CouponType': ('优惠券的两种计算方式：百分比折扣和固定金额减免。', 'PERCENT 的 value 是百分比数值，不是直接扣除的金额；计算在 CouponService 中完成。'),
 'UserCouponStatus': ('个人优惠券的状态：已发放、已占用、已使用、已过期。', '状态列表并不代表自动运行过期任务；本项目主要在使用时检查有效期。'),
 'CartRepository': ('按用户查找他的购物车主记录。', '一人只有一个购物车由数据库唯一约束兜底；CartService 还按用户串行修改，避免首次并发创建时撞唯一约束。'),
 'CartEntity': ('保存购物车属于哪个用户；商品明细在 cart_items 表。', '购物车不是订单，不保存最终成交金额；下单时仍须重新查询商品价格和库存。'),
 'CartItemRepository': ('查询、保存或删除某个购物车中的商品明细。', '查询必须带 cartId，不能只拿 productId 找明细，否则可能碰到其他用户的购物车。'),
 'CartController': ('接收查看购物车、设置商品数量和移除商品的请求。', '用户 ID 从当前身份取得，不能让请求方随便填写。PUT 设置的是最终数量，不是每重试一次再加一。'),
 'PaymentAttemptEntity': ('保存一次支付尝试的金额、状态、幂等键和支付方流水号。', 'UNKNOWN 代表结果还不知道，不能当作明确拒付。订单与支付分开记录，方便重试和核对。'),
 'PaymentAttemptRepository': ('查询支付记录、加行锁，以及竞争一次支付的执行权。', 'claim 用条件更新把 INITIATED 或过期的 PROCESSING 改成处理中；不同请求不能同时拿到同一次执行权。'),
 'PaymentWebhookRepository': ('登记支付方回调的 eventId，并判断这条回调是否已经处理过。', 'INSERT ON CONFLICT DO NOTHING 让并发相同事件只登记一次；登记与更新支付要在同一事务，失败才能一起撤销。'),
 'PaymentController': ('接收付款、全额退款和模拟支付回调请求。', '用户付款需要 JWT；支付方回调使用 HMAC 签名而不是用户登录。两种身份来源不能混为一谈。'),
 'WebhookSignature': ('校验模拟支付回调的签名和时间窗口。', '拿签名与原始请求内容一起验证，防止内容被改。通过验签不代表业务可重复执行，还要用 eventId 去重。'),
 'PaymentStatus': ('支付尝试的状态：刚登记、处理中、成功、明确拒付、结果未知。', '状态必须区分“失败”和“还不知道”；超时只能说明没有及时取得结果，不能证明没有扣款。'),
 'RefundEntity': ('保存一次全额退款的归属、金额、状态和退款方流水号。', 'INITIATED 只有成功领取后才变 PROCESSING；UNKNOWN 必须核对，不能换个键盲目重新退款。'),
 'RefundRepository': ('按支付和幂等键查退款，并能锁住一条退款记录。', '重试需要找回原退款；数据库另限制同一笔支付只能有一条未明确失败的退款，避免重复退钱。'),
 'RefundTransactionService': ('用短数据库事务登记退款、领取执行权、保存退款结果。', '真正调用支付方在 RefundService 中进行。拆成两个 Spring 对象，使调用经过事务代理，而不是同一对象自己调用自己。'),
 'AuditLogEntity': ('保存一次业务操作的操作者、资源、前后摘要和关联编号。', '审计记录用于追查谁做过什么，不是任意内容的备份；不能把密码、Token 或完整支付数据塞进摘要。'),
 'AuditLogRepository': ('把审计记录追加到 audit_log 表。', '审计是业务事实的一部分，调用方应明确让它加入哪个事务；有这张表不等于已经具备防篡改审计系统。'),
 'IdempotencyRecordEntity': ('保存下单幂等键、请求指纹、处理状态和最终订单 ID。', '相同键重试复用原订单；相同键却更换商品必须拒绝。expiresAt 只是数据字段，当前没有自动清理或到期复用任务。'),
 'IdempotencyRecordRepository': ('按用户 ID 与幂等键查找已经登记的下单请求。', '不同用户可使用同一字符串键，因此不能只按 key 查询。数据库唯一约束和事务锁共同保护并发下单。'),
 'OrderRepository': ('查询订单、按用户分页，并在修改订单前锁住订单行。', '取消与支付可能同时发生；先锁住同一订单，再判断状态，避免双方都依据过期状态继续执行。'),
 'OrderItemRepository': ('按订单 ID 取出成交明细，并按明细 ID 返回稳定顺序。', '这些明细保存历史快照，不应在读历史订单时重新拿商品当前价格计算金额。'),
 'OrderDtos': ('规定下单请求和订单响应的字段。', '请求只接收商品、数量和优惠券，不接收用户 ID 或最终价格。响应包含后端算出的金额和成交快照。'),
 'OrderController': ('订单 HTTP 入口：创建订单、查询自己的订单和取消未付款订单。', '当前用户由 CurrentUser 取得，幂等键从请求头取得；具体计价、锁和事务由应用服务完成。'),
 'OrderMapper': ('把订单主记录和成交明细转换成接口响应。', '转换对象不应再查数据库或重新计价；这样历史订单返回的金额来自保存的成交事实。'),
 'RequestFingerprint': ('把下单的关键内容转换成稳定的 SHA-256 请求指纹。', '先合并和排序商品，再算指纹；仅改变商品输入顺序不应被误判为另一种业务请求。哈希不是对请求内容加密。'),
 'OrderCommandService': ('取消订单，并归还预留库存、释放尚未使用的优惠券。', '先锁单、查权限和未终结支付，再改变状态。重复取消不会重复归还；结果未知的支付不能直接按未付款取消。'),
 'OrderQueryService': ('查订单、组装明细，并判断当前用户能否读取或修改该订单。', '“能查别人的订单”和“能修改别人的订单”是两种权限；客服读权限不能直接复用成写权限。'),
 'OrderStatus': ('列出订单允许使用的状态名称。', '枚举不会自己执行状态变化；要读 OrderEntity 的动作方法。FULFILLING 和 COMPLETED 是预留状态，当前没有完整发货接口。'),
 'OutboxEventRepository': ('保存待发送的业务事件到 outbox_events 表。', '事件必须和订单等业务修改一起落库；后台领取和发布状态的更新由 OutboxJdbcRepository 负责。'),
 'OutboxEventEntity': ('保存一封待寄的业务消息：事件编号、类型、内容、重试次数和领取人。', '事件先留在数据库里，程序重启后还可继续发送。PUBLISHED 只说明发布成功，不代表下游业务已经处理成功。'),
 'InventoryEntity': ('保存一种商品的可售数量 available 和已预留数量 reserved。', '下单时从可售转到预留，付款时只减少预留。管理员调整 available 不是调整总仓库数量，不能把已预留部分也算进去。'),
 'InventoryController': ('库存 HTTP 入口：读取库存，或由管理员设置可售数量。', '数量是否合法是输入校验，能不能修改是权限校验；下单预留通过订单业务调用，不允许随便暴露裸扣库存接口。'),
}
for name, (purpose, why) in comments.items():
    paths = list(JAVA.rglob(name + '.java'))
    assert len(paths) == 1, name
    p = paths[0]
    t = p.read_text()
    m = re.search(r'/\*\*[\s\S]*?\*/', t)
    assert m, name
    old = m.group()
    doc = old[old.index(' * <p><strong>对应文档'):]
    new = '/**\n * ' + purpose + '\n *\n * <p><strong>作用：</strong>' + purpose + '\n *\n * <p><strong>为什么：</strong>' + why + '\n *\n' + doc
    p.write_text(t[:m.start()] + new + t[m.end():])

def replace(path, old, new):
    p = ROOT / path
    t = p.read_text()
    assert old in t, (path, old[:90])
    p.write_text(t.replace(old, new))

replace('mini-commerce/docs/BEGINNER-START-HERE.md', '''用户发请求
→ Controller 接住请求
→ Service 执行业务规则
→ Repository 读写数据库
→ Redis 加速部分读取
→ RabbitMQ 处理异步任务
→ 测试证明规则没有被破坏
→ 日志、指标和链路帮助排错''', '''用户发请求
→ Controller 接住请求
→ Service 执行业务规则
→ Repository 读写数据库
→ 返回 HTTP 响应''')
replace('mini-commerce/docs/BEGINNER-START-HERE.md', '## 一、先记住四句话', '''上面是一次普通请求的主线，不是所有组件排成的一条流水线。

Redis 只参与某些缓存或限流操作；RabbitMQ 的消费者通常在另一个时间处理消息。
测试是开发者在验证项目时运行的程序，不是每个用户请求都会经过的业务步骤。
日志、指标和链路则在程序运行过程中记录线索，帮助排错。

## 一、先记住四句话''')
replace('mini-commerce/docs/BEGINNER-START-HERE.md','domain/         业务状态','domain/          业务状态')
replace('mini-commerce/docs/BEGINNER-START-HERE.md','这个方法里的数据库修改作为一个整体提交；未捕获的运行时异常会触发默认回滚，受检异常需显式设置回滚规则。','把参与同一数据库事务的修改放在一起处理。默认遇到没有被吞掉的运行时异常或 Error，会一起撤销；受检异常要另外声明回滚规则。')
replace('mini-commerce/docs/BEGINNER-START-HERE.md','完整说明见：[Spring 与 Java 注解小白词典]', '''这里的前提是调用真正经过 Spring 的事务代理。“代理”可以先理解成包在业务对象外面的事务助手；你自己 new 一个对象或在同一对象内部调用，不会自动增加这一层帮助。事务也不能撤销已发送的外部 HTTP 请求。

完整说明见：[Spring 与 Java 注解小白词典]''')
replace('mini-commerce/docs/SPRING-JAVA-ANNOTATIONS.md','GET /api/orders/8f2...','GET /api/orders/550e8400-e29b-41d4-a716-446655440000')
replace('mini-commerce/docs/SPRING-JAVA-ANNOTATIONS.md','路径中的完整 UUID 字符串会转换成 UUID 对象。','这是格式示例，不保证数据库里存在该订单；实际操作请用创建接口返回的 id。路径中的完整 UUID 字符串会转换成 UUID 对象。')
replace('mini-commerce/docs/SPRING-JAVA-ANNOTATIONS.md','- 方法执行很慢，下一轮不断积压；','- fixedDelay 方法执行很慢，会让下一次执行推迟，消息积压可能继续增加；')
replace('mini-commerce/docs/SPRING-JAVA-ANNOTATIONS.md','- 把失败异常完全吞掉，导致任务悄悄停止工作。','- 把异常吞掉且不记录日志，任务可能每轮都失败，但你看不见原因。吞掉异常本身并不等于调度器停止运行。')
replace('mini-commerce/docs/SPRING-JAVA-ANNOTATIONS.md','表示名称不能超过 100 个字符。','表示名称长度不能超过 100（Java String 按 UTF-16 单元计数，某些 emoji 占两个）。@Size 单独允许 null，必填字符串还要配合 @NotBlank。')
replace('mini-commerce/docs/SPRING-JAVA-ANNOTATIONS.md','> 数字必须大于 0。','> 非 null 数字必须大于 0。包装类型如 Integer 的必填还要配合 @NotNull；int 本身不能保存 null。')
replace('mini-commerce/docs/SPRING-JAVA-ANNOTATIONS.md','> 数字必须大于等于 0。','> 非 null 数字必须大于等于 0；它本身不代表字段必填。')
replace('mini-commerce/docs/SPRING-JAVA-ANNOTATIONS.md','如果请求不符合要求，通常直接返回 400，不再继续执行创建业务。','如果请求不符合要求，通常直接返回 400，不再继续执行创建业务。这里是 Spring MVC 在接收请求时触发校验；普通 Java 代码直接调用一个带 @Valid 参数的方法，不会仅因为这个标签就自动校验。')
replace('mini-commerce/docs/SPRING-JAVA-ANNOTATIONS.md','> 给整个 Controller 规定一个共同的 URL 开头。','> 放在 Controller 类上时，规定共同的 URL 开头；也可以放在方法上，指定更具体的路径、HTTP 方法等匹配条件。')
replace('mini-commerce/docs/SPRING-JAVA-ANNOTATIONS.md','> 第一次保存实体时，自动记录创建时间。','> 配合已启用的 Spring Data 审计和实体监听器，在创建时记录时间。仅加这个标签不够；本项目 BaseEntity 实际使用的是 @PrePersist。')
replace('mini-commerce/docs/SPRING-JAVA-ANNOTATIONS.md','> 每次修改实体时，自动更新最后修改时间。','> 配合已启用的 Spring Data 审计和实体监听器，记录修改时间；本项目实际使用 @PreUpdate。原生 UPDATE 不会自动调用实体回调。')
replace('mini-commerce/docs/JAVA-SYNTAX-FOR-BACKEND-BEGINNERS.md','price.multiply(quantity)','price.multiply(BigDecimal.valueOf(quantity))')
replace('mini-commerce/docs/JAVA-SYNTAX-FOR-BACKEND-BEGINNERS.md','不要用 `==` 比较 `BigDecimal`。','不要用 `==` 比较 BigDecimal。只比较数值是否相等可用 a.compareTo(b) == 0；equals 还比较小数位，1.0 和 1.00 的 equals 为 false。quantity 是 int 时，先转换成 BigDecimal 再 multiply。')
replace('mini-commerce/docs/JAVA-SYNTAX-FOR-BACKEND-BEGINNERS.md','`record` 适合 DTO、配置和事件数据，但不代表所有业务对象都应该写成 record。','record 适合 DTO、配置和事件数据，但不代表所有业务对象都应该写成 record。它只是字段引用不可重新赋值；字段里的 List 仍可能被修改，需要时要防御性复制。自动 toString 会展示字段，所以不要把含密码或 Token 的请求、配置 record 整个写入日志。')
p=ROOT/'mkdocs.yml';t=p.read_text();t=t.replace('exclude_docs: |\n  FULL_BOOK.md\n  MANIFEST.md\n  00_原始学习路线.md\n','');p.write_text(t)
p=JAVA/'shared/error/GlobalExceptionHandler.java';t=p.read_text();old='''    /**
     * 最后的安全网：处理前面没有明确分类的异常。
     *
     * <p>这不代表可以忽略未知异常。这里会记录完整服务端日志，并向客户端返回不泄露内部细节的 500。
     */''';assert old in t;t=t.replace(old,'    /** 处理 JSON 格式、必填请求头和路径参数类型错误；这些是 400，不是服务器 500。 */');t=t.replace('    @ExceptionHandler(Exception.class)','    /** 最后的安全网：未知错误记录服务端堆栈，对调用方只返回安全的 500 提示。 */\n    @ExceptionHandler(Exception.class)');p.write_text(t)
p=JAVA/'shared/redis/RateLimitService.java';t=p.read_text().replace('Redis 故障策略由调用方区分：登录可保守拒绝，普通读接口可受控 Fail Open。','Redis 故障时，当前登录入口拒绝继续；下单入口放行，但仍依赖数据库幂等和库存保护。这不是全站限流。');p.write_text(t)
p=ROOT/'tools/generate_annotation_usage_index.py';t=p.read_text().replace('from pathlib import Path','from pathlib import Path\n\nfrom java_source_scan import annotations');start=t.index('        for line_number, line in enumerate(text.splitlines(), start=1):');end=t.index('    return dict(sorted(usages.items()))',start);t=t[:start]+'''        for name, line_number in annotations(text):
            usages[name].append({"path": relative, "line": line_number})
'''+t[end:];t=t.replace('> 本文件由 `tools/generate_annotation_usage_index.py` 自动生成。','> 本文件由 `tools/generate_annotation_usage_index.py` 自动生成，仅统计代码中的注解，不统计注释和字符串提及。');p.write_text(t)
p=DOCS/'SPRING-JAVA-ANNOTATIONS.md';p.write_text(p.read_text()+(ROOT/'tools/maintenance/annotation-supplement.md').read_text());(ROOT/'tools/maintenance/annotation-supplement.md').unlink()
p=ROOT/'mini-commerce/backend/src/test/java/com/example/minicommerce/BusinessSafetyIT.java';t=p.read_text();i=t.rfind('}');t=t[:i]+'''
    @Autowired com.example.minicommerce.cart.application.CartService carts;

    @Test
    void concurrentFirstCartPutCreatesOnlyOneCartAndOneLine() throws Exception {
        try (var pool = java.util.concurrent.Executors.newFixedThreadPool(2)) {
            var start = new java.util.concurrent.CountDownLatch(1);
            java.util.concurrent.Callable<Long> put = () -> {
                start.await();
                return carts.put(buyer.id(), productId, 2).cartId();
            };
            var first = pool.submit(put);
            var second = pool.submit(put);
            start.countDown();
            assertThat(first.get(10, java.util.concurrent.TimeUnit.SECONDS))
                    .isEqualTo(second.get(10, java.util.concurrent.TimeUnit.SECONDS));
        }
        assertThat(carts.get(buyer.id()).items()).hasSize(1);
        assertThat(carts.get(buyer.id()).items().getFirst().quantity()).isEqualTo(2);
        assertThat(jdbc.queryForObject("select count(*) from carts where user_id=?",
                Integer.class, buyer.id())).isEqualTo(1);
        assertThat(inventory.findById(productId).orElseThrow().getReserved()).isZero();
    }

    @Test
    void invalidCartQuantityDoesNotCreateAnyRecord() {
        assertThatThrownBy(() -> carts.put(buyer.id(), productId, 0))
                .isInstanceOf(BusinessException.class);
        assertThat(carts.get(buyer.id()).items()).isEmpty();
    }
'''+t[i:];p.write_text(t)
print('Applied reviewed explanations, dictionaries and regression tests; validation follows.')
