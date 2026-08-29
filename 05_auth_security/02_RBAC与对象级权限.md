# RBAC 与对象级权限

> **所属模块：** 05 Security
> **本文用途：** 防止已登录用户横向越权，并让管理员权限可分级和审计。
> **前置知识：** 认证基础
> **建议投入：** 阅读 3 小时，实践 5 小时

---

## 一、RBAC

```text
User → Role → Permission
```

角色便于分配，权限表达能力：

```text
USER: ORDER_READ_OWN, ORDER_CANCEL_OWN
ADMIN: PRODUCT_WRITE, ORDER_READ_ALL
SUPPORT: ORDER_READ_LIMITED
```

不要在所有业务代码中硬编码 `role == ADMIN`。

## 二、对象级权限

Alice 已登录请求 `/orders/999`，若 999 属于 Bob，仅检查 USER Role 会泄露数据。

需要：

```java
orderAuthorization.canRead(currentUser, order)
```

或查询直接带：

```sql
WHERE order_id=? AND user_id=?
```

## 三、前端不是安全边界

隐藏删除按钮只改善体验。攻击者可直接调用 API；后端必须强制授权。

## 四、粗粒度与细粒度

方法注解适合权限：

```java
@PreAuthorize("hasAuthority('PRODUCT_WRITE')")
```

对象所有权、订单状态等在业务 Policy 中检查。

## 五、404 或 403

403 明确存在但禁止；404 隐藏存在性。按安全和产品策略统一。

## 六、高风险权限

退款审批、用户禁用、生产发布、IAM 变更应：细分、重新认证、审批、审计。MCP 默认不能拥有管理员能力。

## 七、权限矩阵

每个新 API 明确未登录、本人、他人、不同角色、批量场景。批量操作需逐个资源验证。

## 八、审计

记录 Actor、Action、Resource、Result、Reason、traceId、时间。权限拒绝也可按风险统计。
