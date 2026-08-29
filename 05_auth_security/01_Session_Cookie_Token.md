# Session、Cookie 与 Token 生命周期

> **所属模块：** 05 Security
> **本文用途：** 理解登录、凭证传播、过期、刷新、撤销和退出。
> **前置知识：** HTTP
> **建议投入：** 阅读 4 小时，实践 5 小时

---

## 一、Session

```text
验证凭证
→ 服务端创建 Session
→ Cookie 保存 Session ID
→ 后续请求自动携带 Cookie
```

优点：服务端易撤销、状态集中。代价：多实例共享 Session、Cookie 场景需 CSRF 防护。

## 二、Cookie 安全属性

- HttpOnly：JS 不能直接读取；不能阻止 XSS 代替用户发请求；
- Secure：只通过 HTTPS；
- SameSite：限制跨站携带，是 CSRF 防线之一；
- Domain/Path：越小越好；
- Max-Age：生命周期。

## 三、Bearer Token / JWT

谁持有 Bearer Token，谁就能调用。

JWT 要验证签名、算法、Issuer、Audience、Expiration、Not Before 和 Key Rotation。Payload 通常只是编码，不是秘密容器。

不要把密码、私密资料放 JWT。

## 四、Access / Refresh

Access 短期用于 API；Refresh 长期换新 Access，风险更高，需要轮换、撤销和安全存储。

```text
Login
→ Access + Refresh
→ Access 过期
→ Refresh Rotation
→ 新 Access/Refresh
```

## 五、浏览器存储

- HttpOnly Cookie：降低 JS 读取风险，但处理 CSRF；
- Memory：刷新丢失，需要恢复；
- localStorage：简单，但 XSS 可读取。

没有万能答案，要基于威胁模型。

## 六、Logout

Session：删除服务端 Session + 清 Cookie。

Token：删除客户端、撤销 Refresh；已发 Access 在短过期内可能仍有效。

## 七、密码

成熟哈希、独立 Salt、登录限速、重置 Token 一次性短期、不要泄露账号是否存在、高风险操作重新认证。

## 八、OAuth2/OIDC

OAuth2 处理授权委托；OIDC 增加身份层。Google 登录要验证 Provider、Audience、Nonce 等，不自己发明协议。

## 九、测试

登录成功/失败、过期、Refresh、重放、Logout、用户禁用、角色变化、多设备、时钟偏差、Key Rotation。
