# Spring 请求生命周期与 IoC / DI

> **所属模块：** 02 Backend
> **本文用途：** 理解框架怎样路由请求、管理对象和注入依赖，以及这些机制为什么影响测试与事务。
> **前置知识：** HTTP 基础
> **建议投入：** 阅读 3 小时，实验 3 小时

---

## 一、一次请求

```text
Embedded Server
→ Filter Chain
→ DispatcherServlet
→ Handler Mapping
→ 参数绑定与校验
→ Controller
→ Service
→ Repository
→ JSON 序列化
```

Spring Boot 替你完成服务器启动、组件扫描、路由、参数绑定、序列化和异常转换。理解这些边界，才能在 401、校验、Controller 和数据库错误之间定位。

## 二、IoC

传统：

```java
class ProductController {
    private final ProductService service = new ProductService();
}
```

Controller 自己决定依赖怎样创建。

IoC：由 Spring 容器创建和管理对象，再交给使用者。

```java
@RestController
class ProductController {
    private final ProductService service;

    ProductController(ProductService service) {
        this.service = service;
    }
}
```

## 三、DI

依赖注入让类只声明“需要什么”，不负责“如何构造”。

构造器注入优点：

- 依赖在类型签名中可见；
- 字段可 `final`；
- 对象创建后完整；
- 测试可直接传 Fake/Mock；
- 依赖过多会暴露职责膨胀。

避免字段注入：它隐藏依赖、依赖反射、测试不自然。

## 四、Bean 与注解

常见：

```text
@Component
@Service
@Repository
@RestController
@Configuration
@Bean
```

`@Service` 不只是装饰，它向人和 AI 表达语义。

## 五、不是所有类都应由 Spring 管理

适合 Bean：

- Service；
- Repository；
- 外部 Client；
- 配置；
- 有生命周期的组件。

普通 Value Object、DTO、临时对象直接 `new` 即可。

## 六、接口不要机械创建

每个 `FooService` 都配 `FooServiceImpl`，但只有一个实现且无边界价值，会增加样板。

接口适合：

- 多实现；
- 外部系统 Port；
- 稳定模块契约；
- 测试替代；
- 插件机制。

## 七、单例 Bean 的并发风险

Spring Bean 默认常为单例。不要保存请求级可变状态：

```java
@Service
class BadService {
    private Long currentUserId; // 多请求共享
}
```

请求数据应作为参数或使用明确 Scope。

## 八、代理陷阱

事务、安全、缓存等注解经常依赖代理。

```java
public void outer() { inner(); }

@Transactional
public void inner() {}
```

同对象内部调用可能绕过代理，事务不生效。关键注解必须用集成测试证明，而不是只看代码。

## 九、实验

- 删除 `@Service`，观察启动失败；
- 创建两个同类型 Bean，观察歧义；
- 用构造器传 Fake；
- 比较字段注入与构造器注入测试；
- 复现事务自调用问题。

## 十、自测

1. IoC 与 DI 的关系？
2. Controller 为什么不自己 `new Service`？
3. 哪些对象不需要 Bean？
4. 单例 Bean 为什么不能保存 currentUser？
5. 每个 Service 都建接口有什么代价？
