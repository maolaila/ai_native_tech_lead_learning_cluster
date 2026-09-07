
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
