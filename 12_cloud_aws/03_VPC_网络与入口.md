# VPC、Subnet、Security Group 与互联网入口

> **所属模块：** 12 Cloud
> **本文用途：** 理解公网/私网、路由、入口和出站，避免把数据库直接暴露。
> **前置知识：** 网络基础
> **建议投入：** 阅读 5 小时，画图 4 小时

---

## 一、基础

```text
Internet
→ Route 53
→ CloudFront/WAF（可选）
→ Public ALB
→ Private ECS Tasks
→ Private RDS/Redis
```

VPC 是逻辑网络；Subnet 是 AZ 内网段；Route Table 决定流量去向。

## 二、Public / Private

Public Subnet 有到 Internet Gateway 的路由；Private 资源不接受公网直接入口。RDS/Redis 通常 Private，Security Group 只允许应用来源。

## 三、Security Group

有状态防火墙。优先引用另一个 Security Group：

```text
ALB SG → ECS SG:8080
ECS SG → RDS SG:5432
ECS SG → Redis SG:6379
```

不要开放 `0.0.0.0/0:5432`。

## 四、NAT

Private Subnet 资源访问公网需要 NAT Gateway/其他方案。NAT 有固定成本和流量成本；应明确哪些服务需要出站，必要时用 VPC Endpoint。

## 五、ALB

TLS、健康检查、Path/Host 路由、目标组、滚动/蓝绿支持。Health Path 要轻量且表达 Readiness。

## 六、CloudFront

静态前端、图片和可缓存 GET；Cache Key 包含必要 Query/Header/Cookie，避免把用户私有响应缓存给别人。

## 七、TLS

ACM 管理证书；HTTPS；安全 Header；Origin 通信按需求加密。不要把证书私钥手工塞容器。

## 八、出站控制

SSRF 风险下，只允许必要域名/网段、阻止元数据和私网访问，使用 Endpoint/Proxy/Firewall。应用级 URL 校验与网络限制配合。

## 九、排障

DNS→ALB Listener→Target Health→SG→Route→Task Port→Application Health→Dependency。Flow Logs/ALB Logs/CloudWatch/Trace 结合。

## 十、多 AZ

将 ALB/Tasks 跨至少两个 AZ；RDS Multi-AZ。仍需测试 AZ 失效和容量是否足够。
