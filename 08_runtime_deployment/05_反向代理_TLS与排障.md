# 反向代理、TLS 与部署网络排障

> **所属模块：** 08 Runtime
> **本文用途：** 把域名、HTTPS、代理、应用和依赖串起来，定位 502/504 等问题。
> **前置知识：** HTTP/网络、Docker
> **建议投入：** 阅读 4 小时，实践 6 小时

---

## 一、拓扑

```text
Browser
→ DNS
→ CDN / Load Balancer
→ TLS Termination
→ Reverse Proxy
→ Frontend / API
→ PostgreSQL/Redis/RabbitMQ
```

## 二、代理职责

TLS、Host/Path 路由、静态文件、压缩、Body Limit、Timeout、WebSocket、限流、负载均衡、转发 Header。

## 三、Forwarded Headers

代理后应用看到的 Remote IP/Protocol 可能是代理地址/HTTP。需要正确处理：

```text
X-Forwarded-For
X-Forwarded-Proto
X-Forwarded-Host
```

但只信任受控代理，不能盲信客户端伪造 Header。

## 四、TLS

证书要匹配域名、有效期、完整 Chain；HTTP 跳 HTTPS；Cookie Secure；内部是否 TLS 按威胁模型。

## 五、502 与 504

- 502：代理无法得到有效上游响应，如未监听、连接拒绝、协议错误；
- 504：代理等待上游超时。

先看代理日志和上游健康，而不是只重启浏览器。

## 六、超时预算

外层 Timeout 应大于内层，但总预算明确：

```text
Client 5s
Proxy 4.5s
Application 4s
DB 1s
External API 1.5s
```

重试会放大总耗时和负载。

## 七、排障案例

### 本机 API 正常，域名 502

查 DNS→Proxy 配置→Upstream Host/Port→容器网络→Readiness→应用日志。

### HTTP 正常，HTTPS 失败

查证书、SNI、Chain、443 监听、防火墙、TLS 版本。

### 只有大文件失败

查 Body Size、Proxy Timeout、应用 Multipart、临时磁盘、对象存储。

### 登录后循环跳转

查 Forwarded Proto、Cookie Domain/SameSite/Secure、Session Store、时钟。
