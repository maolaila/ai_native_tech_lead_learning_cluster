# Web 常见攻击与防御

> **所属模块：** 05 Security
> **本文用途：** 通过攻击路径理解 SQL Injection、XSS、CSRF、SSRF、越权和业务逻辑滥用。
> **前置知识：** 认证授权
> **建议投入：** 阅读 5 小时，本地实验 6 小时

---

## SQL Injection

字符串拼 SQL：

```java
"SELECT * FROM users WHERE email='" + email + "'"
```

使用参数化查询、白名单动态列、最小 DB 权限。ORM 不是绝对免疫，Native SQL 仍可出错。

## XSS

不可信 HTML 在用户浏览器执行。使用框架转义、上下文编码、富文本 Sanitization、CSP，避免危险 HTML API。

HttpOnly 可降低 Token 被直接读取，但恶意脚本仍可能以用户身份操作。

## CSRF

浏览器自动带 Cookie，攻击页面可诱导跨站请求。防御：CSRF Token、SameSite、Origin 检查、敏感操作重新认证，不用 GET 修改状态。

## SSRF

后端替用户抓 URL，攻击者访问：

```text
127.0.0.1
内网地址
云元数据地址
```

使用 Allowlist、校验最终 IP/重定向、禁止私网段、出站网络限制、Timeout/Size Limit。

## Broken Access Control

改变 ID 访问他人数据。默认拒绝、对象级权限、权限测试和审计。

## Mass Assignment

Request 直接绑定 Entity，攻击者提交 `role=ADMIN`。使用专用 DTO 和白名单。

## 文件上传

限制大小/类型、随机名、对象存储、隔离扫描、禁止执行、不信任原始文件名。

## 路径/命令注入

`../../etc/passwd`、拼 Shell Command。规范化路径、固定根、避免 Shell、参数化 Process API。

## 业务逻辑攻击

无限领券、并发用券、重复库存恢复、篡改金额、重放支付。需要状态机、事务、幂等、唯一约束和测试，WAF 不能替代。

## 限流

登录、验证码、重置、高成本 API；按 user/IP/tenant/API key 组合，不能只依赖单一 IP。
