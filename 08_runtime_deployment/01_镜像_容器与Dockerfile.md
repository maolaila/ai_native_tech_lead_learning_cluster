# 镜像、容器与 Dockerfile

> **所属模块：** 08 Runtime
> **本文用途：** 理解不可变镜像、多阶段构建、缓存、非 root 和可重复 Build。
> **前置知识：** Linux 基础
> **建议投入：** 阅读 4 小时，实践 6 小时

---

## 一、心智模型

- Image：只读模板和层；
- Container：镜像运行后的进程和可写层；
- Registry：存储与分发镜像；
- Volume：独立于容器生命周期的数据；
- Network：容器间可解析和通信的网络。

删除 Container 不等于删除 Image/Volume；重建 Container 后可写层会消失。

## 二、为什么镜像

“在我机器上能跑”常依赖隐式环境。镜像把 OS 用户空间、Runtime、依赖和应用打成可识别 Artifact，方便本地、CI、Staging、Production 运行同一内容。

## 三、多阶段构建

Java 示例：

```dockerfile
FROM eclipse-temurin:21-jdk AS build
WORKDIR /workspace
COPY mvnw pom.xml ./
COPY .mvn .mvn
RUN ./mvnw -q -DskipTests dependency:go-offline
COPY src src
RUN ./mvnw -q -DskipTests package

FROM eclipse-temurin:21-jre
WORKDIR /app
RUN useradd --system --uid 10001 app
COPY --from=build /workspace/target/*.jar app.jar
USER 10001
EXPOSE 8080
ENTRYPOINT ["java","-jar","/app/app.jar"]
```

Build 工具不进入运行镜像，减少体积和攻击面。

## 四、Layer Cache

先复制依赖描述并下载依赖，再复制变化频繁的源代码。否则每次代码变化都重新下载全部依赖。

## 五、`.dockerignore`

排除：`.git`、`node_modules`、`target`、日志、IDE 配置、Secret、本地数据。减少 Build Context 和泄露风险。

## 六、版本

基础镜像固定可审查标签，关键环境可固定 Digest。不要让 `latest` 在不同时间产生不同构建。

## 七、非 root

应用通常不需要 root。若攻击者利用应用漏洞，非 root 限制破坏范围。还应只读文件系统、最小 Capabilities、限制资源和扫描镜像。

## 八、不要把配置写死进镜像

同一镜像跨环境，Config/Secret 在运行时注入。前端静态 Build 若嵌入变量，要明确其构建时性质。

## 九、PID 1 与 ENTRYPOINT

Exec Form 让 Java/Node 直接接收 TERM；Shell Form 可能让 Shell 成为 PID1，信号和退出码处理复杂。

## 十、实验

- 对比单阶段和多阶段大小；
- 修改一行代码观察 Cache；
- 进入 Container 看运行用户；
- 删除 Container 后观察内部文件消失；
- 用 Digest 标记 Artifact。
