# Spring 请求生命周期与 IoC / DI

> **所属模块：** 02 Backend
> **本文用途：** 理解框架怎样路由请求、管理对象和注入依赖，以及这些机制为什么影响测试与事务。
> **前置知识：** HTTP 基础
> **建议投入：** 阅读 3 小时，实验 3 小时

> 后端零基础先读：[后端零基础：从这里开始](../mini-commerce/docs/BEGINNER-START-HERE.md) 和 [Spring 与 Java 注解小白词典](../mini-commerce/docs/SPRING-JAVA-ANNOTATIONS.md)。

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

先用大白话理解：

```text
内置服务器收到请求
→ 过滤器先检查请求
→ Spring 找到应该处理这个 URL 的 Controller 方法
→ 把 URL、Header 和 JSON 转成 Java 参数
→ Controller 调用 Service
→ Service 调用 Repository
→ 结果转成 JSON 返回
```

Spring Boot 替你完成服务器启动、组件扫描、路由、参数绑定、序列化和异常转换。理解这些边界，才能在 401、校验、Controller 和数据库错误之间定位。

如果上面的英文名暂时记不住，不影响第一遍学习。先记住：

> 请求不是直接跳进业务代码，中间还会经过服务器、过滤器、路由和参数转换。

## 二、IoC

IoC 全称 Inversion of Control，中文常叫“控制反转”。名字比较抽象，先这样理解：

> 一个类需要哪些其他对象，由 Spring 负责创建和组合，而不是这个类自己到处 `new`。

传统写法：

```java
class ProductController {
    private final ProductService service = new ProductService();
}
```

Controller 自己决定依赖怎样创建。以后 `ProductService` 还需要数据库、缓存和配置时，Controller 也被迫知道这些细节。

IoC 写法：

```java
@RestController
class ProductController {
    private final ProductService service;

    ProductController(ProductService service) {
        this.service = service;
    }
}
```

Controller 只说“我需要 ProductService”，Spring 负责找到并传进来。

## 三、DI

DI 全称 Dependency Injection，中文叫“依赖注入”。

可以把 IoC 和 DI 的关系先记成：

```text
IoC：把创建和管理对象的工作交给 Spring
DI：Spring 把一个类需要的对象传给它
```

构造器注入优点：

- 依赖在构造器中一眼可见；
- 字段可以写成 `final`；
- 对象创建完成时依赖已经齐全；
- 测试可以直接传 Fake 或 Mock；
- 构造器参数太多时，会提醒这个类可能承担了太多职责。

避免字段注入：它隐藏依赖、依赖反射，脱离 Spring 时不方便直接创建和测试。

## 四、Bean 与注解

Bean 可以先理解成：

> 由 Spring 创建并管理的 Java 对象。

常见标签：

```text
@Component      普通 Spring 组件
@Service        主要负责业务操作
@Repository     主要负责数据库访问
@RestController 主要负责 HTTP 接口
@Configuration  主要负责集中配置
@Bean           把方法返回的对象交给 Spring 管理
```

`@Service` 不只是装饰，它向人和工具表达“这个类主要负责业务”。但加上它不会自动让类设计合理，也不会自动开启事务。

## 五、不是所有类都应由 Spring 管理

适合 Bean：

- Service；
- Repository；
- 外部 Client；
- 配置；
- 有明确生命周期的组件。

普通 Value Object、DTO、临时对象直接 `new` 即可。

如果什么都交给 Spring，会让简单对象也依赖容器，测试和理解反而更复杂。

## 六、接口不要机械创建

每个 `FooService` 都配 `FooServiceImpl`，但只有一个实现且没有边界价值，会增加样板代码。

接口适合：

- 确实有多个实现；
- 外部系统 Port，例如真实支付和模拟支付；
- 稳定模块契约；
- 测试需要替代实现；
- 插件机制。

接口不是“高级代码”的标志。它应该解决替换、隔离或契约问题。

## 七、单例 Bean 的并发风险

Spring Bean 默认常为单例。大白话：

> 整个应用中很多请求会共同使用同一个 Service 对象。

因此不要把某个请求的用户 ID 保存到 Service 字段：

```java
@Service
class BadService {
    private Long currentUserId; // 多个请求会共同读写
}
```

请求数据应作为方法参数传递，或者使用明确的请求级上下文。

## 八、代理陷阱

事务、安全、缓存等注解经常依赖 Spring 代理。

代理可以先理解成：

> Spring 在真实对象外面包一层。调用方法前后，这一层负责开启事务、检查权限或处理缓存。

```java
public void outer() {
    inner();
}

@Transactional
public void inner() {
}
```

同一个对象内部直接调用 `inner()`，可能没有经过外面的 Spring 代理，所以事务可能不生效。

关键注解必须用集成测试证明，而不是只看代码上写了注解。

## 九、本项目中的对应位置

```text
mini-commerce/backend/src/main/java/com/example/minicommerce/MiniCommerceApplication.java
mini-commerce/backend/src/main/java/com/example/minicommerce/order/api/OrderController.java
mini-commerce/backend/src/main/java/com/example/minicommerce/order/application/CreateOrderService.java
mini-commerce/backend/src/main/java/com/example/minicommerce/shared/config/AppProperties.java
```

完整请求走读：

[一次创建订单请求：从 HTTP 到数据库](../mini-commerce/docs/REQUEST-TO-DATABASE-WALKTHROUGH.md)

## 十、实验

- 删除一个 `@Service`，观察依赖是否无法创建；
- 创建两个同类型 Bean，观察 Spring 怎样报告歧义；
- 不启动 Spring，直接通过构造器传 Fake；
- 比较字段注入与构造器注入测试；
- 复现事务自调用问题。

每次实验只改变一个条件，记录：

```text
我改了什么
→ 发生了什么
→ 为什么
→ 改回去后是否恢复
```

## 十一、自测

1. IoC 与 DI 的关系？
2. Controller 为什么不自己 `new Service`？
3. Bean 用大白话怎样解释？
4. 哪些对象不需要 Spring 管理？
5. 单例 Bean 为什么不能保存 currentUserId？
6. 每个 Service 都建接口有什么代价？
7. 为什么同类内部调用可能让 `@Transactional` 不生效？
