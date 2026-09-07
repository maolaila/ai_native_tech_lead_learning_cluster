# 模块 05：认证、授权与应用安全

> 阅读定位：本模块同时包含原理、当前参考实现和后续练习。验收清单是你的学习目标，不表示这些能力都已在工程中完成；实际可运行范围见 [正式学习说明](../mini-commerce/docs/LEARNING-READINESS.md)。

> **所属模块：** 05 Security
> **本文用途：** 建立身份和权限边界，识别常见 Web、Secret 与供应链风险。
> **前置知识：** 后端、数据库、测试
> **建议投入：** 3 周

---

```text
Authentication：你是谁
Authorization：你能做什么
```

已登录不等于能读任意订单；前端隐藏按钮不等于安全控制。

文件：

1. [`01_Session_Cookie_Token.md`](01_Session_Cookie_Token.md)
2. [`02_RBAC与对象级权限.md`](02_RBAC与对象级权限.md)
3. [`03_Web常见攻击.md`](03_Web常见攻击.md)
4. [`04_Secret与供应链.md`](04_Secret与供应链.md)
5. [`05_实操与验收.md`](05_实操与验收.md)

目标不是渗透专家，而是能设计登录生命周期、RBAC、对象权限、Secret、CI/MCP 最小权限，并在 Review 中发现高风险问题。
