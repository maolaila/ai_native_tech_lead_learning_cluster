# Compose、Network、Volume 与 Health Check

> **所属模块：** 08 Runtime
> **本文用途：** 一键启动完整项目，并正确理解服务名、依赖就绪和持久数据。
> **前置知识：** Dockerfile
> **建议投入：** 阅读 4 小时，配置 8 小时

---

## 一、Compose 的作用

```yaml
services:
  api:
  postgres:
  redis:
  rabbitmq:
  prometheus:
  grafana:
```

把本地拓扑作为代码，方便新人、CI 和故障实验。

## 二、服务名就是 DNS

同一 Compose 网络：

```text
api → postgres:5432
api → redis:6379
api → rabbitmq:5672
```

容器里 `localhost` 是自身。

## 三、端口

只在宿主需要访问时发布：

```yaml
ports:
  - "8080:8080"
```

数据库若仅供内部使用，不必生产暴露公网端口。

## 四、Volume

```yaml
volumes:
  postgres-data:
```

将数据库数据放在容器外。删除 Container 不丢；删除 Volume 会丢。本地恢复演练应故意删除后从备份恢复。

Bind Mount 适合源码开发；Named Volume 适合运行数据。

## 五、启动顺序不等于就绪

`depends_on` 只表示启动关系；PostgreSQL 进程启动后可能仍未 Ready。使用 Health Check 和应用连接重试。

```yaml
healthcheck:
  test: ["CMD-SHELL", "pg_isready -U app -d commerce"]
  interval: 5s
  timeout: 3s
  retries: 20
```

## 六、Health 层次

- Container 进程存在；
- Liveness；
- Readiness；
- Dependency Health；
- Business Smoke。

健康接口不能只返回硬编码 200，但也不能因可降级缓存挂掉就无限重启。

## 七、资源限制

本地也可限制 CPU/Memory，提前暴露内存假设和资源耗尽行为。

## 八、日志

应用输出 stdout/stderr，由运行平台收集。不要把无限增长日志只写容器内部文件。

## 九、常见问题

- 错用 localhost；
- Volume 权限；
- DB 尚未 Ready；
- 端口冲突；
- 配置在宿主有、容器没有；
- 健康检查命令不存在；
- 服务健康但业务不可用。
