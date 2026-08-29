# 配置、Secret 与环境分离

> **所属模块：** 08 Runtime
> **本文用途：** 让同一 Artifact 在不同环境运行，并防止配置漂移和凭证泄露。
> **前置知识：** Docker/安全
> **建议投入：** 阅读 3 小时，实践 4 小时

---

## 一、代码、配置、Secret、数据

```text
Code：业务逻辑
Config：环境参数
Secret：需要保密的凭证
Data：运行状态
```

四者生命周期不同，不能全部烘焙进镜像。

## 二、环境变量

```text
SPRING_DATASOURCE_URL
SPRING_DATASOURCE_USERNAME
PAYMENT_READ_TIMEOUT
```

好处是通用；缺点是类型弱、嵌套复杂、可能从进程环境泄露。应用启动时类型化绑定和 Fail Fast。

## 三、`.env.example`

```dotenv
POSTGRES_DB=commerce
POSTGRES_USER=commerce_app
POSTGRES_PASSWORD=change-me
```

只放占位和说明，不放真实值。

## 四、Secret

生产使用平台 Secret Store，要求加密、权限、审计、轮换、版本和访问日志。

不要：

- Dockerfile `ENV PASSWORD=...`；
- Image Layer 中复制 `.env`；
- 前端变量存真正 Secret；
- CI Echo；
- 错误响应返回连接串。

## 五、Profiles

`local/staging/prod` 可以选择不同配置，但不要形成三套行为完全不同的应用。核心业务和依赖形态尽量一致。

## 六、配置漂移

服务器手工改配置会让“Git 与实际生产”不一致。配置应版本化或受管理，并能追踪谁在何时改了什么。

## 七、启动校验

关键配置缺失、Timeout 非法、URL 错误，应启动失败，而不是第一笔真实请求时才发现。

## 八、Feature Flag

用于渐进开放和紧急关闭，不用于永久维护两套杂乱逻辑。每个 Flag 有 Owner、目的、默认、失效日期和清理任务。

## 九、时区与 Locale

容器通常 UTC；业务展示按用户/业务时区转换。不要依赖“开发电脑是日本时区”这一隐式条件。
