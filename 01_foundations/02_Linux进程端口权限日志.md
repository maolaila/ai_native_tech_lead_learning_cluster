# Linux：进程、端口、权限与日志

> **所属模块：** 01 Foundations
> **本文用途：** 掌握应用离开 IDE 后最常见的运行观察手段。
> **前置知识：** 基础命令行
> **建议投入：** 阅读 2 小时，实验 3 小时

---

## 一、应用首先是进程

Spring Boot 启动后是 Java 进程，会占 CPU、内存，监听端口，读取配置，创建连接并输出日志。

常用：

```bash
ps aux | grep java
top
free -h
df -h
ss -lntp
lsof -i :8080
```

## 二、日志

```bash
less application.log
tail -n 200 application.log
tail -f application.log
grep -n 'orderId=123' application.log
journalctl -u mini-commerce --since '10 minutes ago'
```

坏日志：

```text
error happened
```

好日志至少有：

```text
level=ERROR event=order_creation_failed traceId=... userId=42 orderId=123 reason=inventory_conflict
```

## 三、Signal 与关闭

```bash
kill -TERM <pid>
```

给应用机会停止接流量、完成正在执行请求、关闭连接和刷新日志。

```bash
kill -KILL <pid>
```

立即终止，不能清理。除非进程完全不响应，否则不应作为默认操作。

## 四、权限

```bash
ls -l
chmod 640 application.yml
chown app:app application.yml
```

不要用 `chmod 777` 作为万能修复。应用应以非 root 用户运行，只拥有完成任务所需权限。

## 五、环境变量

```bash
printenv
echo "$JAVA_HOME"
export APP_ENV=local
```

数据库密码不能硬编码或写日志。配置和代码的生命周期不同。

## 六、固定排障法

访问 `server:8080` 失败：

1. `ps`：进程在吗？
2. `ss`：端口监听吗？
3. 本机 `curl 127.0.0.1:8080/health`；
4. `journalctl` / logs；
5. 本机成功而远程失败，再看网络和防火墙。

## 七、常见事故

- 磁盘满导致日志和数据库写失败；
- 内存不足被 OOM Killer 终止；
- 旧进程占端口；
- 服务启动后因数据库错误立即退出；
- 日志无限增长；
- Secret 被打印。

## 八、自测

1. 进程存在但端口未监听说明什么？
2. 本机 curl 成功、远程失败查什么？
3. TERM 为何优于 KILL？
4. 磁盘满会表现成哪些应用问题？
5. Jenkins 显示成功为什么不代表应用健康？
