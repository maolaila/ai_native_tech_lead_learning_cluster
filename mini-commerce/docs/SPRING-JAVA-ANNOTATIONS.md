# Spring 与 Java 注解小白词典

这份词典专门解释项目里常见的 `@Something`。

先把注解理解成：

> **贴在类、方法或字段上的说明标签。** Spring、JPA、测试框架看到这些标签后，会按约定做额外工作。

注解本身通常不是业务逻辑。它更像是告诉框架：“请把这个类当成什么”“这个方法应该怎样运行”“这个字段怎样保存到数据库”。

---

## 一、程序启动与配置

## `@SpringBootApplication`

### 它是什么

Spring Boot 应用最常见的启动注解。

### 大白话

> 告诉 Spring Boot：“从这里启动程序，并自动准备常用的 Web、配置、数据库等能力。”

### 项目位置

`backend/src/main/java/com/example/minicommerce/MiniCommerceApplication.java`

### 你现在先记住

它通常只放在主启动类上，不要到处添加。

---

## `@ConfigurationPropertiesScan`

### 大白话

> 告诉 Spring：“请扫描项目中的 `@ConfigurationProperties` 配置类，并把配置文件里的值装进去。”

### 为什么项目使用它

项目把 JWT、支付、缓存和 Outbox 配置集中放在 `AppProperties` 中，避免很多业务类各自写一串 `@Value`。

---

## `@ConfigurationProperties(prefix = "app")`

### 它是什么

把一组配置绑定到一个 Java 对象。

### 大白话

> 把配置文件中所有以 `app` 开头的内容，按名字装进这个对象。

例如配置文件：

```yaml
app:
  payment:
    connect-timeout: 2s
    read-timeout: 5s
```

Java：

```java
@ConfigurationProperties(prefix = "app")
public record AppProperties(
        Jwt jwt,
        Payment payment,
        Cache cache,
        Outbox outbox) {
}
```

Spring 会把：

```text
app.payment.connect-timeout
```

放进：

```java
AppProperties.Payment.connectTimeout
```

### 为什么比到处写 `@Value` 更适合本项目

- 同一类配置集中在一起；
- 字段有明确类型，例如 `Duration`；
- 配置改名时更容易统一检查；
- 测试时更容易构造配置对象；
- 不会在业务类中散落很多字符串路径。

### 项目位置

`shared/config/AppProperties.java`

---

## `@Value`

### 它是什么

从配置文件或环境变量中取一个值，放到字段或参数里。

### 大白话

```java
@Value("${app.example.timeout-ms:3000}")
private long timeoutMillis;
```

可以读成：

> 程序启动时读取示例配置 app.example.timeout-ms；没有配置时使用 3000 毫秒。这是语法示例，不是本项目实际支付超时字段。

### `${...}` 是什么

`${...}` 表示“按照这个名字去配置中查找”。

### 默认值怎么写

```java
@Value("${app.example.timeout-ms:3000}")
```

冒号后面的 `3000` 是默认值（单位由本示例约定为毫秒）：

> 配置存在就用配置；配置不存在就使用 3000 毫秒。Duration 的 3s 简写绑定由 Spring Boot 的 @ConfigurationProperties 支持，不要把所有 @Value 转换能力与它等同。

### 常见错误

1. 配置名写错，程序启动失败；
2. 到处散落 `@Value`，后面很难统一修改；
3. 把密码直接写进注解默认值并提交到 Git；
4. 以为 `@Value` 会自动保证配置一定合理，它只负责取值，不代表值符合业务要求。

### 本项目为什么较少直接使用

本项目主要用 `@ConfigurationProperties` 管理成组配置。`@Value` 仍然需要认识，因为很多 Spring 项目和文档会使用它。

---

## `@Configuration`

### 大白话

> 这个类主要用来集中告诉 Spring：系统需要创建哪些对象，以及这些对象怎样组合。

常见于安全、Redis、RabbitMQ 等配置类。

---

## `@Bean`

### 大白话

> 把这个方法返回的对象交给 Spring 管理，其他类以后可以直接使用它。

例如：

```java
@Bean
Clock clock() {
    return Clock.systemUTC();
}
```

以后需要 `Clock` 的类，不必自己 `new`，Spring 会把这个对象传进去。

### 为什么这样做

测试时可以把真实时钟换成固定时钟，让“当前时间”相关测试可重复。

---

## `@EnableScheduling`

### 大白话

> 打开定时任务功能，让项目中的 `@Scheduled` 方法可以按时间自动执行。

本项目的 Outbox 发布器会定期检查是否有待发送消息。

---

## `@Scheduled`

### 大白话

> 不需要人手调用，Spring 会按照设定的时间间隔自动运行这个方法。

例如：

```java
@Scheduled(fixedDelayString = "${app.outbox.poll-delay:1s}")
public void publishBatch() {
}
```

意思是：上一次执行结束后，等待一段时间，再执行下一次。

### 常见错误

- fixedDelay 方法执行很慢，会让下一次执行推迟，消息积压可能继续增加；
- 多实例同时执行，却没有领取锁或幂等保护；
- 把异常吞掉且不记录日志，任务可能每轮都失败，但你看不见原因。吞掉异常本身并不等于调度器停止运行。

---

## 二、Spring 管理的业务对象

## `@Component`

### 大白话

> 告诉 Spring：“请创建并管理这个普通组件。”

它是一个通用标签。

---

## `@Service`

### 大白话

> 告诉 Spring：“这个类主要负责业务操作。”

它本质上也是 Spring 管理的组件，但名字更能表达用途。

### 项目例子

```java
@Service
public class CreateOrderService {
}
```

### 常见错误

不要因为加了 `@Service`，就把所有代码都塞进一个超大类。它只说明类的角色，不会自动让设计变好。

---

## `@Repository`

### 大白话

> 这个类主要负责访问数据库。

Spring Data JPA 接口通常不需要手写 `@Repository`，因为 Spring 会自动识别继承 `JpaRepository` 的接口。

---

## 三、HTTP 接口相关注解

## `@RestController`

### 大白话

> 这个类负责接收 HTTP 请求，方法返回值通常会自动转成 JSON。

### 项目例子

```java
@RestController
@RequestMapping("/api/orders")
public class OrderController {
}
```

---

## `@RequestMapping`

### 大白话

> 放在 Controller 类上时，规定共同的 URL 开头；也可以放在方法上，指定更具体的路径、HTTP 方法等匹配条件。

```java
@RequestMapping("/api/orders")
```

表示这个类中的接口通常都以 `/api/orders` 开头。

---

## `@GetMapping`

### 大白话

> 这个方法处理 HTTP GET 请求，通常用于查询数据。

```java
@GetMapping("/{id}")
```

可能对应：

```text
GET /api/orders/550e8400-e29b-41d4-a716-446655440000
```

---

## `@PostMapping`

### 大白话

> 这个方法处理 HTTP POST 请求，通常用于创建数据或执行一个业务动作。

例如创建订单：

```java
@PostMapping
public OrderResponse create(...) {
}
```

---

## `@PutMapping`

### 大白话

> 这个方法处理 HTTP PUT 请求，通常用于整体更新一项资源。

---

## `@DeleteMapping`

### 大白话

> 这个方法处理 HTTP DELETE 请求，通常用于删除资源。

业务系统中有些“删除”实际是状态变更，不一定真的从数据库物理删除。

---

## `@PathVariable`

### 大白话

> 从 URL 路径中取值。

```java
@GetMapping("/{id}")
public OrderResponse get(@PathVariable UUID id) {
}
```

请求：

```text
GET /api/orders/550e8400-e29b-41d4-a716-446655440000
```

这是格式示例，不保证数据库里存在该订单；实际操作请用创建接口返回的 id。路径中的完整 UUID 字符串会转换成 UUID 对象。这里不能填 `123`：它不是合法 UUID，本项目会返回 400。

---

## `@RequestParam`

### 大白话

> 从 URL 问号后面的查询参数中取值。

```text
GET /api/products?page=0&size=20
```

`page` 和 `size` 就是查询参数。

---

## `@RequestHeader`

### 大白话

> 从 HTTP 请求头中取值。

项目创建订单时：

```java
@RequestHeader("Idempotency-Key") String key
```

表示从请求头读取幂等键，用来防止重复下单。

---

## `@RequestBody`

### 大白话

> 把请求中的 JSON 内容转换成 Java 对象。

```java
@RequestBody CreateOrderRequest request
```

例如请求 JSON：

```json
{
  "items": [
    {"productId": 1, "quantity": 2}
  ]
}
```

会被转换成 `CreateOrderRequest`。

---

## `@ResponseStatus`

### 大白话

> 指定接口成功时返回哪个 HTTP 状态码。

```java
@ResponseStatus(HttpStatus.CREATED)
```

常见返回为 `201 Created`，表示创建成功。

---

## `@PageableDefault`

### 大白话

> 给分页查询提供默认页大小和默认排序。

```java
@PageableDefault(size = 20, sort = "createdAt") Pageable pageable
```

表示调用者没有传分页参数时，默认每页 20 条，并按创建时间排序。

---

## 四、参数校验注解

## `@Valid`

### 大白话

> 在进入业务方法前，先检查请求对象上的校验规则。

```java
public ProductResponse create(@Valid @RequestBody CreateProductRequest request)
```

如果请求不符合要求，通常直接返回 400，不再继续执行创建业务。这里是 Spring MVC 在接收请求时触发校验；普通 Java 代码直接调用一个带 @Valid 参数的方法，不会仅因为这个标签就自动校验。

---

## `@NotNull`

> 这个值不能是 `null`。

---

## `@NotBlank`

> 字符串不能是 `null`、空字符串，也不能只包含空格。

---

## `@Size`

> 限制字符串或集合的最小、最大长度。

```java
@Size(max = 100)
String name
```

表示名称长度不能超过 100（Java String 按 UTF-16 单元计数，某些 emoji 占两个）。@Size 单独允许 null，必填字符串还要配合 @NotBlank。

---

## `@Positive`

> 非 null 数字必须大于 0。包装类型如 Integer 的必填还要配合 @NotNull；int 本身不能保存 null。

---

## `@PositiveOrZero`

> 非 null 数字必须大于等于 0；它本身不代表字段必填。

### 重要提醒

参数校验只负责检查输入格式。像“优惠券是否属于当前用户”“订单是否允许取消”这样的业务规则，仍然要在业务层检查。

---

## 五、事务注解

## `@Transactional`

### 它是什么

把一组数据库操作放进同一个事务。

### 大白话

> 方法里的关键数据库修改要一起成功；中途抛出符合回滚条件的异常时，一起撤销。

### 项目例子

创建订单时需要同时完成：

```text
保存幂等记录
+ 占用优惠券
+ 预留库存
+ 保存订单
+ 保存订单项快照
+ 写入 Outbox
```

任何一步失败，前面已经做的数据库修改都应回滚。

### `readOnly = true`

```java
@Transactional(readOnly = true)
```

大白话：

> 这个方法主要用于读取，不准备修改数据。

它是给框架和开发者的提示，也可能带来一些优化，但不要把它理解成绝对安全锁。

### 最常见误区

1. **以为加了事务就不会超卖。** 错。两个事务仍可能并发，需要条件更新、锁或版本控制；
2. **同一个类内部自己调用自己的事务方法。** 可能绕过 Spring 代理，事务不按预期生效；
3. **把很慢的外部 HTTP 调用放进事务。** 会长时间占用数据库连接和锁；
4. **捕获异常后不再抛出。** Spring 可能认为方法正常结束，从而提交事务；
5. **事务范围过大。** 会增加锁等待和失败影响范围。

---

## 六、JPA 与数据库映射注解

## `@Entity`

### 大白话

> 告诉 JPA：“这个 Java 类需要和数据库表对应。”

`Entity` 可以理解成数据库记录在 Java 中的表示。

---

## `@Table`

### 大白话

> 指定这个实体对应哪张表，以及表上的部分约束。

```java
@Table(name = "cart_items")
```

表示对应数据库表 `cart_items`。

---

## `@Id`

### 大白话

> 这个字段是主键，用来唯一确定一条数据库记录。

---

## `@GeneratedValue`

### 大白话

> 新增记录时，主键值由指定规则生成。

```java
@GeneratedValue(strategy = GenerationType.IDENTITY)
```

通常表示数据库使用自增方式产生 ID。

---

## `@Column`

### 大白话

> 说明 Java 字段怎样对应数据库列。

```java
@Column(name = "product_id", nullable = false)
private Long productId;
```

表示：

- 数据库列名是 `product_id`；
- 不允许保存 `null`。

### 常见参数

- `name`：数据库列名；
- `nullable = false`：不允许为空；
- `length`：字符串最大长度提示；
- `unique = true`：要求唯一。

重要唯一规则最好仍通过 Flyway Migration 明确创建并命名，方便审查和发布。

---

## `@UniqueConstraint`

### 大白话

> 告诉数据库：某些列的组合不能重复。

购物车中：

```text
cart_id + product_id
```

不能重复，避免同一个购物车出现两条完全相同的商品明细。

应用层“先查再插”不能完全挡住并发，数据库唯一约束才是最后一道防线。

---

## `@Enumerated(EnumType.STRING)`

### 大白话

> Java 枚举保存到数据库时，使用名称字符串，而不是数字位置。

例如保存 `PAID`，而不是保存 `2`。

为什么通常更安全：枚举顺序调整后，字符串含义仍然清楚；数字位置可能悄悄变错。

---

## `@Version`

### 大白话

> 给记录增加版本号，用来发现“别人已经先修改过这条数据”。

这叫乐观锁。更新时版本不对，说明当前数据已经不是你读取时的那一版。

---

## `@MappedSuperclass`

### 大白话

> 这个父类本身通常不单独对应一张表，但它的字段会被子实体继承到各自的表中。

项目中的 `BaseEntity` 用它统一保存创建时间和更新时间等字段。

---

## `@EntityListeners`

### 大白话

> 当实体保存、更新等事件发生时，让指定监听器帮忙做额外处理。

常用于自动填写创建时间和更新时间。

---

## `@CreatedDate`

> 配合已启用的 Spring Data 审计和实体监听器，在创建时记录时间。仅加这个标签不够；本项目 BaseEntity 实际使用的是 @PrePersist。

## `@LastModifiedDate`

> 配合已启用的 Spring Data 审计和实体监听器，记录修改时间；本项目实际使用 @PreUpdate。原生 UPDATE 不会自动调用实体回调。

---

## `@Transient`

### 大白话

> 这个字段只是 Java 运行时临时使用，不保存到数据库。

注意它和 Java 的 `transient` 关键字不是完全同一个概念。

---

## 七、Repository 与 SQL 注解

## `@Query`

### 大白话

> 不使用 Spring 自动推导的方法名，而是明确写出要执行的查询或更新语句。

可以写 JPQL，也可以写原生 SQL。

---

## `nativeQuery = true`

### 大白话

> `@Query` 里面写的是数据库真正执行的 SQL，而不是面向 Java 实体的 JPQL。

本项目库存条件更新使用原生 PostgreSQL SQL，因为需要精确控制：

```sql
available >= :qty
```

只有库存足够时才扣减。

---

## `@Modifying`

### 大白话

> 这条 `@Query` 不是普通查询，而是会修改数据库的 UPDATE 或 DELETE。

没有它，Spring Data JPA 可能把语句当成查询处理。

---

## `@Param`

### 大白话

> 把 Java 方法参数绑定到查询中的命名占位符。

```java
@Param("qty") int quantity
```

对应 SQL 中的：

```sql
:qty
```

---

## `@Lock(LockModeType.PESSIMISTIC_WRITE)`

### 大白话

> 查询这条记录时先加写锁，其他事务想修改同一条记录时需要等待。

这叫悲观锁：先假设可能发生冲突，所以先锁住。

### 注意

锁不是越多越安全。锁范围太大、持有时间太长，会降低并发并增加死锁风险。

---

## 八、安全相关注解

## `@EnableMethodSecurity`

### 大白话

> 打开方法级权限判断，使 `@PreAuthorize` 等注解可以生效。

---

## `@PreAuthorize`

### 大白话

> 在方法真正执行前，先检查当前用户是否满足权限条件。

例如：

```java
@PreAuthorize("hasRole('ADMIN')")
```

表示只有管理员角色可以调用。

### 重要提醒

角色权限不等于对象权限。普通用户即使可以“查看订单”，也只能查看自己的订单，仍需检查订单归属。

---

## `@AuthenticationPrincipal`

### 大白话

> 从 Spring Security 当前登录信息中取出用户对象。

本项目部分位置使用 `CurrentUser` 统一封装当前用户读取，避免 Controller 重复处理安全上下文。

---

## `@Order`

### 大白话

> 当多个过滤器、处理器或配置需要按顺序执行时，指定先后次序。

数字越小通常越先执行，但要结合具体框架位置理解。

---

## 九、异常处理注解

## `@RestControllerAdvice`

### 大白话

> 集中处理所有 Controller 抛出的异常，并统一转换成 JSON 错误响应。

这样每个 Controller 不需要重复写 `try/catch`。

---

## `@ExceptionHandler`

### 大白话

> 指定某个方法专门处理哪一类异常。

例如业务异常、参数校验异常、找不到资源等，可以转换成统一错误码和 HTTP 状态。

---

## 十、RabbitMQ 相关注解

## `@RabbitListener`

### 大白话

> 监听指定 RabbitMQ 队列。队列中有消息时，Spring 会自动调用这个方法。

### 常见错误

- 以为消息只会收到一次；
- 业务已提交但 Ack 丢失时，消息可能再次投递；
- 没做幂等，导致积分、通知或扣款重复执行；
- 捕获异常却告诉 Broker 已成功，消息会被错误丢弃。

---

## 十一、测试常见注解

## `@Test`

> 这个方法是一条自动化测试。

---

## `@SpringBootTest`

### 大白话

> 启动较完整的 Spring 应用环境进行测试。

它比纯单元测试更慢，适合验证多个组件组合后的行为。

---

## `@DataJpaTest`

### 大白话

> 主要启动 JPA 和数据库相关部分，用于测试 Repository 和实体映射。

---

## `@Testcontainers`

### 大白话

> 测试时通过容器启动真实依赖，例如 PostgreSQL。

这样可以避免只在内存数据库上通过、到了真实 PostgreSQL 却失败。

---

## `@Container`

> 这个字段表示一个由 Testcontainers 管理的测试容器。

---

## `@BeforeEach`

> 每条测试运行前都执行一次，常用于准备干净数据。

## `@AfterEach`

> 每条测试运行后执行一次，常用于清理资源。

---

## 十二、看注解时的固定判断方法

每遇到一个注解，只问四个问题：

1. 它贴在类、方法、参数还是字段上？
2. 是 Spring、JPA、校验框架、消息框架还是测试框架提供的？
3. 它让框架额外做了什么？
4. 如果去掉它，程序会怎样变化？

不要一上来研究注解源码。先理解它在当前业务流程中的作用。

## 十三、项目中的注解使用位置

自动扫描结果见：

[注解使用位置索引](generated/annotation-usage-index.md)

该索引会列出每种注解在哪些 Java 文件中出现，方便你从词典跳回真实代码。

## 验收补充：几个容易学错的标签

**`@Transactional(propagation = Propagation.MANDATORY)`：**调用者必须已经开启数据库事务；没有就报错。库存预留必须和订单在同一事务，不能单独提交。

**`@Transactional(rollbackFor = Exception.class)`：**本项目消息与回调处理还会抛出 JSON 解析等受检异常，因此显式要求它们回滚。默认规则是 RuntimeException 和 Error 回滚，而不是“任何异常都会回滚”。本项目采用默认代理模式，同一对象内部自调用不会经过事务代理；退款拆成 RefundService 与 RefundTransactionService 正是为了保证这一点。

**`@JdbcTypeCode(SqlTypes.CHAR)`：**Hibernate 扩展，明确告诉它数据库列是 CHAR。本项目币种列是 CHAR(3)，Java String 的默认 VARCHAR 映射并不等于 CHAR；真实数据库的 ddl-auto=validate 会核对映射。

**`@DirtiesContext`：**通知 Spring 测试框架丢弃旧的应用上下文。集成测试的每个测试类会重启 PostgreSQL 容器；不能把指向旧容器端口的连接池继续用于下一个类。这会增加测试启动时间，但避免错误复用。

**`@Modifying` 的 flush 与 clear：**flush 把已跟踪的修改发给数据库，事务尚可回滚；clear 使整个上下文里的对象脱离跟踪，不等于只刷新某条库存。现在的库存更新不再全局 clear。

参考：[Spring 事务注解规则](https://docs.spring.io/spring-framework/reference/data-access/transaction/declarative/annotations.html)、[Spring Data JPA 修改查询](https://docs.spring.io/spring-data/jpa/reference/jpa/query-methods.html)。

## 十四、项目实际使用但初版漏讲的注解

这些不是要求你今天全部记住。遇到名称时，在本页搜索，再通过[注解位置索引](generated/annotation-usage-index.md)返回正在读的文件。

| 注解 | 通俗作用、项目位置与容易误解的地方 |
|---|---|
| `@Autowired` | 让 Spring 把已有对象交给当前对象；在集成测试中取得真实服务。业务类只有一个构造器时，通常省略该标签也能构造器注入；自己 new 不会触发注入。 |
| `@Profile` | 只在指定运行模式启用这个组件，例如 DemoDataInitializer 只在 local 创建演示账号。Profile 不是权限系统，不能靠叫 prod 就自动变安全。 |
| `@ConditionalOnProperty` | 根据配置决定是否创建组件；OutboxPublisher 可以通过开关停用。它在启动时判断，不是每次调用都读取一次开关。 |
| `@PrePersist` | JPA 插入新实体前执行这个方法；BaseEntity 在这里填写时间。直接执行 SQL 不会调用它。 |
| `@PreUpdate` | JPA 更新实体前执行；BaseEntity 用它更新时间。没有实际更新，或直接执行原生 SQL，不保证经过它。 |
| `@Index` | 在实体映射里描述索引；本项目真正创建索引的是 Flyway SQL，不是启动时靠标签自动建。 |
| `@Email` | 检查字符串是否像邮箱地址；不发送验证邮件，也不证明地址属于注册者。必填还要配合 NotBlank。 |
| `@NotEmpty` | 集合、字符串或数组不能为 null，也不能长度为零。与 NotBlank 不同：空格字符串不算长度为零。订单 items 使用它。 |
| `@Pattern` | 字符串需匹配给出的规则。币种用 [A-Z]{3} 检查三个大写字母，但这不能证明它是真实存在的币种。 |
| `@DecimalMin` | 非 null 金额不能小于给定下限，默认包含下限。商品 price 至少为 0.01；必填仍配合 NotNull。 |
| `@Digits` | 限制整数和小数部分位数，让商品价格符合 numeric(19,2)。它不负责自动四舍五入。 |
| `@Override` | 请 Java 编译器检查：这个方法确实是在实现或覆盖父类型的方法。拼错名字时及时报错；它不是 Spring 功能。 |
| `@SuppressWarnings` | 关闭明确指定的编译警告。它不修复错误，也不会把运行风险变安全；应理解警告原因再使用。 |
| `@AutoConfigureMockMvc` | 在 Spring 集成测试里准备 MockMvc，用模拟 HTTP 请求经过控制器和过滤链。它不是浏览器，也不等于真正经过网络端口的 Smoke。 |
| `@MockitoBean` | 在 Spring 测试环境里，把指定依赖替换成可控制的假对象。本项目部分 HTTP 测试替换限流；这不能证明真实 Redis 已工作，另用 Compose 验证。 |
| `@ActiveProfiles` | 为测试选择配置模式，例如 test。test 配置补充和覆盖 application.yml；不应为了测试通过而意外隐藏主配置错误。 |
| `@DynamicPropertySource` | 在测试启动 Spring 前动态提供配置。容器数据库端口每次可能不同，这里把实际地址交给连接池。 |
| `@AnalyzeClasses` | 告诉 ArchUnit 读取哪些 Java 包的依赖关系。它是检查代码结构，不是启动整个系统。 |
| `@ArchTest` | 把一个架构规则交给 ArchUnit 运行，比如 Controller 不得直接依赖 Repository。它不能证明金额计算或事务正确。 |

### 参数校验不是自动修正数据

`@Size`、`@Pattern`、`@Email`、`@Digits` 和数字范围约束通常允许 null；必填另用 `@NotNull` 或 `@NotBlank`。订单的 `List<@NotNull @Valid OrderLineRequest>` 同时要求每项非空，并继续检查每项内部的字段。

### 同名注解要看 import

本文的 `@Value` 是 Spring 的配置注入标签，不是 Lombok 的同名标签。`@Transactional` 指 `org.springframework.transaction.annotation.Transactional`，不要直接替换成其他包里的同名标签。

### Entity 标签不是数据库迁移

本项目 `ddl-auto=validate` 的意思是“检查数据库与映射是否匹配”，不是自动创建或升级表。`@Table`、`@Column(nullable=false)`、`@Index`、`@UniqueConstraint` 只是映射声明；数据库是否真的有非空、唯一、索引约束，要看 Flyway SQL 或实际数据库结构。

官方核对入口（已在本仓库解释，不必现在打开）：[Spring 事务规则](https://docs.spring.io/spring-framework/reference/data-access/transaction/declarative/annotations.html)、[Spring Boot 外部配置](https://docs.spring.io/spring-boot/3.5/reference/features/external-config.html)、[Jakarta Validation 规范](https://jakarta.ee/specifications/bean-validation/3.0/jakarta-bean-validation-spec-3.0.html)。
