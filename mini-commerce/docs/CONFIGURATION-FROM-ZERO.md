# Spring 配置从零开始：`application.yml`、环境变量、`@Value` 与 `@ConfigurationProperties`

这份说明专门解决一个常见困惑：

> 配置文件里的值，究竟怎样进入 Java 代码？

---

## 一、什么是配置

配置是“不同环境可能变化，但不应该写死在业务代码里的值”。

例如：

- 数据库地址；
- Redis 地址；
- RabbitMQ 地址；
- JWT 有效期；
- 支付连接超时；
- 缓存过期时间；
- Outbox 每次处理多少条消息。

不应该这样写：

```java
Duration readTimeout = Duration.ofSeconds(5);
```

因为开发环境、测试环境和生产环境可能需要不同值。

更常见的是把它放到配置中：

```yaml
app:
  payment:
    read-timeout: 5s
```

---

## 二、`application.yml` 是什么

Spring Boot 默认会读取：

```text
src/main/resources/application.yml
```

YAML 通过缩进表示层级：

```yaml
app:
  payment:
    connect-timeout: 2s
    read-timeout: 5s
```

可以理解成：

```text
app.payment.connect-timeout = 2s
app.payment.read-timeout = 5s
```

### 缩进为什么重要

下面两个配置不是一回事：

```yaml
app:
  payment:
    read-timeout: 5s
```

```yaml
app:
payment:
  read-timeout: 5s
```

第二个写法中 `payment` 已经不属于 `app`。

YAML 建议只使用空格，不使用 Tab。

---

## 三、环境变量是什么

环境变量是由操作系统、Docker 或部署平台提供给程序的值。

例如：

```text
DB_HOST=postgres
DB_PASSWORD=example
```

配置文件可以引用环境变量：

```yaml
spring:
  datasource:
    url: jdbc:postgresql://${DB_HOST:localhost}:5432/mini_commerce
    password: ${DB_PASSWORD:postgres}
```

这里：

```text
${DB_HOST:localhost}
```

表示：

> 有 `DB_HOST` 就使用它；没有就使用 `localhost`。

### Secret 为什么更适合环境变量或 Secret 管理服务

密码、API Key、JWT 签名密钥不应该直接写进仓库。部署时可以通过环境变量、Docker Secret、Kubernetes Secret 或云 Secret 管理服务注入。

注意：环境变量也不是绝对安全。它仍然需要正确的主机权限、日志脱敏和部署权限控制。

---

## 四、`@Value` 怎样取一个配置值

```java
@Value("${app.payment.read-timeout}")
private Duration readTimeout;
```

逐段解释：

```text
@Value
```

告诉 Spring：“请给这里填写一个配置值。”

```text
${...}
```

告诉 Spring：“按照括号里的名字去配置中找。”

```text
app.payment.read-timeout
```

是配置路径。

### 带默认值

```java
@Value("${app.payment.read-timeout:3s}")
```

意思是：

```text
找到配置 → 使用配置
找不到配置 → 使用 3 秒
```

### 常见类型转换

Spring 可以把文本配置转换成常见类型：

```text
"true"   → boolean
"20"     → int
"5s"     → Duration
"10MB"   → DataSize
```

如果格式不对，程序可能在启动阶段直接失败。这通常比运行到一半才发现配置错误更好。

---

## 五、本项目为什么不在每个类里到处写 `@Value`

假设支付配置有：

```text
base-url
connect-timeout
read-timeout
webhook-secret
```

如果到处写：

```java
@Value("${app.payment.base-url}")
private URI baseUrl;

@Value("${app.payment.connect-timeout}")
private Duration connectTimeout;

@Value("${app.payment.read-timeout}")
private Duration readTimeout;
```

短期看很直接，但项目变大后会出现：

- 配置路径散落在很多类；
- 改名容易漏改；
- 同一组配置没有集中说明；
- 测试时不方便构造；
- 很难快速知道系统有哪些配置。

所以本项目主要使用：

```java
@ConfigurationProperties(prefix = "app")
public record AppProperties(
        Jwt jwt,
        Payment payment,
        Cache cache,
        Outbox outbox) {
}
```

大白话：

> 把所有 `app.*` 配置集中整理成一个有类型的 Java 对象。

---

## 六、配置名怎样对应 Java 字段

配置：

```yaml
app:
  payment:
    connect-timeout: 2s
    read-timeout: 5s
```

Java：

```java
public record Payment(
        Duration connectTimeout,
        Duration readTimeout) {
}
```

Spring 会把横线命名转换成驼峰命名：

```text
connect-timeout → connectTimeout
read-timeout    → readTimeout
```

---

## 七、`record` 在配置中有什么作用

```java
public record Payment(
        String webhookSecret,
        Duration connectTimeout,
        Duration readTimeout) {
}
```

`record` 适合保存一组配置值，因为它：

- 代码短；
- 构造后不允许随意重新赋值字段；
- 自动提供读取方法；
- 很适合表示“只装数据”的对象。

读取时：

```java
properties.payment().readTimeout()
```

可以读成：

```text
从全部应用配置中
→ 取支付配置
→ 取读取超时时间
```

---

## 八、`@ConfigurationPropertiesScan` 为什么需要

主启动类中：

```java
@ConfigurationPropertiesScan
```

大白话：

> 请 Spring 扫描项目中带有 `@ConfigurationProperties` 的配置类，并让它们生效。

没有正确注册配置类时，Spring 不会自动创建对应配置对象。

---

## 九、Profile 是什么

Profile 可以理解成环境标签。

常见：

```text
local
staging
prod
```

不同 Profile 可以启用不同配置。

例如：

```text
application.yml
application-local.yml
application-prod.yml
```

### 本项目中的作用

本地环境可以创建演示账号和使用本地依赖；生产环境不能自动创建默认账号，也不能使用演示密钥。

### 启用 Profile

```bash
SPRING_PROFILES_ACTIVE=local
```

或：

```bash
java -jar app.jar --spring.profiles.active=local
```

---

## 十、配置覆盖顺序怎么理解

Spring Boot 的完整覆盖规则很多，初学者先记住：

> 越接近当前部署环境、越明确指定的配置，通常优先级越高。

常见来源包括：

```text
application.yml
→ Profile 配置
→ 环境变量
→ 启动命令参数
```

不要依赖记忆猜最终值。排错时应查看启动日志、Actuator 的安全配置端点或明确打印非敏感配置摘要。

绝对不要打印密码、Token 和签名密钥。

---

## 十一、`Duration` 为什么写 `5s` 而不是 `5000`

```yaml
read-timeout: 5s
```

比：

```yaml
read-timeout: 5000
```

更清楚，因为 `5000` 不知道单位是毫秒还是秒。

常见单位：

```text
ms  毫秒
s   秒
m   分钟
h   小时
```

---

## 十二、连接超时和读取超时有什么区别

### Connect Timeout

大白话：

> 最多等多久才能和对方建立网络连接。

### Read Timeout

大白话：

> 连接已经建立后，最多等多久才能收到对方响应数据。

支付等外部调用需要分别设置，避免线程无限等待。

---

## 十三、配置默认值什么时候可以用

适合默认值：

- 本地开发的普通端口；
- 非安全性的轮询间隔；
- 可接受的本地缓存时间。

不适合安全默认值：

- 生产数据库密码；
- JWT 签名密钥；
- 支付 Webhook 密钥；
- 第三方 API Key。

安全配置缺失时，生产环境更合理的做法通常是启动失败，而不是偷偷使用公开默认值。

---

## 十四、配置校验

配置能被读取，不代表配置合理。

例如：

```text
connectTimeout = -1 秒
batchSize = 0
secret = 空字符串
```

项目可以通过 Bean Validation 或构造时检查尽早拒绝非法配置。

初学者先记住：

> 配置错误最好在启动阶段被发现，而不是等用户下单时才爆炸。

---

## 十五、配置与业务代码的边界

配置适合表达：

- 超时时间；
- 批量大小；
- 功能开关；
- 外部服务地址；
- 缓存时间。

不要把核心业务规则随意变成配置，例如：

```text
允许已取消订单继续支付 = true
```

这类规则需要明确业务设计、测试和审计，不能只因为“可配置”就更好。

---

## 十六、排查“配置为什么没有生效”

按顺序检查：

1. 配置路径是否拼写正确；
2. YAML 缩进是否正确；
3. 当前启用了哪个 Profile；
4. 环境变量是否覆盖了文件配置；
5. 配置类是否被 Spring 扫描；
6. 字段类型是否能转换；
7. Docker Compose 是否真的把环境变量传进容器；
8. 修改配置后是否重启了需要重启的进程。

### 不要做的事

不要为了排错把全部环境变量、配置对象和 Secret 打进日志。

---

## 十七、项目中的对应位置

重点查看：

```text
backend/src/main/resources/application.yml
backend/src/main/java/com/example/minicommerce/shared/config/AppProperties.java
backend/src/main/java/com/example/minicommerce/MiniCommerceApplication.java
.env.example
compose.yaml
```

对应文档：

```text
02_backend_spring/05_日志_配置与健康检查.md
08_runtime_deployment/03_配置_Secret与环境.md
```

## 十八、你应该能回答的问题

阅读完成后，不看本文回答：

1. `@Value("${x:y}")` 中 `x` 和 `y` 分别是什么？
2. 为什么本项目主要使用 `@ConfigurationProperties`？
3. `read-timeout: 5s` 怎样进入 `Duration readTimeout`？
4. 为什么 JWT Secret 不应该提供公开默认值？
5. Profile 解决什么问题？
