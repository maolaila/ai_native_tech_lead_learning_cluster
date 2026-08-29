# Rules、Guardrails 与自动执行

> **所属模块：** 13 AI Engineering
> **本文用途：** 将工程原则转换为能在编码、PR、CI 和运行时真正阻止错误的控制。
> **前置知识：** Docs as Code
> **建议投入：** 阅读 5 小时，实现 8 小时

---

## 一、Rule 与 Guardrail

Rule 告诉人/AI 应怎样做；Guardrail 用机制限制不能怎样做。

```text
Rule：Controller 不访问 Repository
Guardrail：ArchUnit / ESLint Boundary Rule 在 CI 阻止
```

只有文档没有 Enforcement，长期会失效。

## 二、分层控制

### Prompt/Instruction

便宜但可忽略，适合指导。

### Template/Generator

把正确结构作为默认，减少自由度。

### Static Analysis

Lint、Type、Architecture、Secret、Dependency、API Compatibility。

### Test/Eval

验证业务和 Agent 行为。

### Permission

限制工具和环境最大破坏范围。

### Human Approval

高风险动作最后一道门。

## 三、规则格式

```yaml
id: BE-ARCH-001
scope: backend/**
statement: Controller must not depend on Repository
rationale: HTTP and persistence changes must not couple
allowed:
  - Controller -> ApplicationService
forbidden:
  - Controller -> *Repository
verification:
  - ArchUnit: ControllerDependencyTest
exception:
  - ADR + Tech Lead approval
severity: blocking
```

## 四、优先级

P0：数据破坏、安全、权限、支付；
P1：架构、兼容、事务、测试；
P2：可维护性；
P3：风格。

不要让 200 条 Style Warning 淹没一个越权漏洞。

## 五、核心 Rules 示例

- 所有 Schema 变更必须 Migration；
- Migration 禁止直接删除仍在用字段；
- 写 API 有 Idempotency 评估；
- 外部调用有 Timeout；
- Retry 写操作必须幂等；
- Payment/Security 需 Code Owner；
- Production DB 不允许 Agent 写；
- 失败测试不得为迎合实现而自动修改；
- 新 API 有 Integration/Contract；
- 日志不得含 Secret。

## 六、例外

规则允许例外，但必须显式：原因、风险、有效期、Owner、替代控制和清理日期。隐藏绕过比有记录例外更危险。

## 七、规则冲突

建立优先级：安全/数据完整性 > 兼容/可靠性 > 架构 > 性能 > 风格。冲突时由人决策并写 ADR。

## 八、质量门禁的渐进上线

先 Warn 收集基线→修存量→对新代码 Block→逐步扩大。第一天把历史项目全部 Block 会促使团队关闭规则。

## 九、规则效果指标

违规率、自动拦截率、误报、例外数量/过期、Review 时间、回归缺陷。无效/高噪规则应改进或删除。
