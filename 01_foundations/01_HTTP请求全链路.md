# HTTP 请求全链路

> **所属模块：** 01 Foundations
> **本文用途：** 把浏览器、网络、服务器和数据库串成一条可排查链路。
> **前置知识：** 前端 Network 基础
> **建议投入：** 阅读 2 小时，实验 2 小时

---

## 一、完整链路

```text
URL 解析
→ DNS：域名到 IP
→ TCP：连接目标 IP:Port
→ TLS：HTTPS 身份与加密
→ HTTP Request
→ CDN / Load Balancer / Reverse Proxy
→ Spring Boot
→ Controller / Service / Repository
→ Connection Pool / PostgreSQL
→ HTTP Response
→ 浏览器渲染
```

同样表现为“页面打不开”，失败层可能完全不同。DNS 失败时应用日志通常没有任何请求；HTTP 500 则说明请求已经到达应用或上游。

## 二、URL

```text
https://shop.example.com:443/products/42?lang=zh#reviews
```

| 部分 | 含义 |
|---|---|
| `https` | Scheme |
| `shop.example.com` | Host |
| `443` | Port |
| `/products/42` | Path |
| `lang=zh` | Query |
| `reviews` | Fragment，通常不发给服务器 |

## 三、Method 与幂等

- GET：读取，不应修改业务状态；
- POST：创建或执行动作，通常非幂等；
- PUT：完整替换，倾向幂等；
- PATCH：部分修改；
- DELETE：删除，通常可设计为幂等。

创建订单若网络响应丢失，客户端会重试。服务端可能已经创建成功，因此需要 Idempotency Key，而不是假设“Timeout 等于失败”。

## 四、状态码

| Code | 场景 |
|---|---|
| 200 | 查询成功 |
| 201 | 创建成功 |
| 204 | 成功无 Body |
| 400 | 参数格式/校验错误 |
| 401 | 未认证 |
| 403 | 已认证但无权限 |
| 404 | 资源不存在 |
| 409 | 状态冲突、重复资源 |
| 429 | 触发限流 |
| 500 | 未处理的服务端错误 |
| 502/504 | 网关与上游异常/超时 |

所有错误都返回 200 会破坏监控、代理、客户端分支和自动重试语义。业务错误码与 HTTP 状态码应协作。

## 五、Header

```http
Content-Type: application/json
Authorization: Bearer ...
Cache-Control: no-store
X-Request-Id: req-123
```

Request/Trace ID 能把前端错误、后端日志、数据库查询和消息处理关联起来。

## 六、Cookie、Session、CORS

Cookie 是浏览器按规则自动携带的数据；Session 通常把登录状态放在服务端，只在 Cookie 中保存 Session ID。

CORS 是浏览器的跨源限制：`curl` 正常、浏览器失败，可能是 CORS 或预检 `OPTIONS` 问题。关闭浏览器安全策略不是修复。

## 七、curl

```bash
curl -v https://example.com
curl -i http://localhost:8080/actuator/health
curl -i -X POST http://localhost:8080/api/orders \
  -H 'Content-Type: application/json' \
  -d '{"items":[{"productId":42,"quantity":2}]}'
```

## 八、排障顺序

```text
URL
→ DNS
→ IP/Port
→ TLS
→ HTTP Status/Body
→ Reverse Proxy
→ 应用日志
→ 数据库/外部依赖
```

不要一开始同时重启所有组件，那会破坏证据。

## 九、自测

1. `Connection refused` 与 HTTP 500 的区别？
2. 为什么 GET 不应删除数据？
3. 401 与 403？
4. 为什么 Timeout 不能证明服务端没成功？
5. `curl` 正常而浏览器失败的可能原因？
