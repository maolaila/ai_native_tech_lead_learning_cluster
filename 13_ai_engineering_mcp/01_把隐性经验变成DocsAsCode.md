# 把隐性经验变成 Docs as Code

> **所属模块：** 13 AI Engineering
> **本文用途：** 把“只有老员工知道”的规则变成可版本化、可检索、可测试的公司知识。
> **前置知识：** 系统设计和生产经验
> **建议投入：** 阅读 4 小时，整理 8 小时

---

## 一、隐性知识的风险

```text
这个字段看似不用，但财务月底导出
这个 API 旧 App 仍调用
这张表不能直接更新
支付回调会重复
这个 Job 每天凌晨占连接
```

只存在人脑里，会造成新人反复犯错、AI 无上下文、Senior 成为瓶颈和离职风险。

## 二、知识分类

### 事实（可自动生成）

API、Schema、模块依赖、配置项、Pipeline、Owner、Runbook Link。

### 决策和原因（人工维护）

ADR、业务不变量、安全政策、失败策略、兼容窗口。

### 操作知识

故障排查、发布、回滚、Migration、DLQ 重放、数据修复。

### 例子

Golden PR、合法/非法实现、历史事故和回归测试。

## 三、最小文档树

```text
docs/
├─ architecture.md
├─ domain-glossary.md
├─ module-map.md
├─ domain-rules/
├─ api/
├─ database/
├─ testing-strategy.md
├─ security.md
├─ deployment.md
├─ observability.md
├─ runbooks/
└─ adr/
```

## 四、怎样写给人和 AI 都能用

坏：

```text
代码要优雅，注意性能。
```

好：

```text
Controller 不得直接依赖 Repository。
新增写 API 必须有 API Integration Test。
订单状态只能通过领域方法转换。
支付回调必须按 providerEventId 幂等。
违反时 CI 失败；例外需 ADR 与 Tech Lead 批准。
```

明确 Scope、Rationale、Allowed、Forbidden、Example、Enforcement、Exception Process。

## 五、知识粒度

不要一次把 500 页文档全部塞上下文。按模块和任务检索最相关片段；内容短、标题清晰、关键词稳定、链接可追溯。

## 六、Single Source of Truth

Schema 从数据库/Migration 生成；API 从 OpenAPI 生成；Pipeline 从代码读取。不要手写第二份容易过期的事实。

## 七、新鲜度

每份文档有 Owner、Last Reviewed、触发更新条件。PR 改 API/Schema/模块时同步改文档；CI 检查链接和必要文件。

## 八、从事故中提炼

事故“重复支付积分”应产出：Regression Test、Unique Constraint、Consumer Rule、Runbook、Eval Case，而不只是 Postmortem。

## 九、第一批最值钱知识

业务不变量、模块 Ownership、禁止跨层、数据库/Migration 规则、权限矩阵、支付/订单幂等、测试策略、发布回滚、生产只读边界、历史事故。
