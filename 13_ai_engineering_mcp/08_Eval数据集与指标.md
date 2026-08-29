# AI Coding Eval 数据集、指标与实验设计

> **所属模块：** 13 AI Engineering
> **本文用途：** 量化 Rules/MCP/Golden Path 是否真正提高新人产能和质量，而不是凭感觉。
> **前置知识：** 测试和 AI 工作流
> **建议投入：** 阅读 6 小时，数据集建设持续

---

## 一、为什么 Eval

“感觉 Claude/Codex 写得不错”不可比较、不可回归、容易只看成功 Demo。Eval 要回答：完成率、质量、风险、人工时间和成本是否改善。

## 二、任务集

覆盖真实工作分布：

### 常规
CRUD、表单、API 字段、分页、权限、日志、Migration。

### 中等
优惠券、订单状态、缓存、消息 Consumer、第三方 API。

### 高风险
越权、并发库存、重复支付、事务部分失败、破坏性 Migration、Secret 泄露。

### Debug
慢 SQL、CORS、配置、Flaky、连接池、DLQ、错误发布。

### 架构
跨模块依赖、API 兼容、选型、Runbook、ADR。

## 三、隐藏测试

Agent 不知道具体 Test，防止只迎合可见断言。来源：业务不变量、历史 Bug、安全规则和故障实验。

## 四、指标

- Requirement Completion；
- Build/Test Pass；
- Hidden Test Pass；
- Defect Severity；
- Security/Architecture Violations；
- Migration/API Compatibility；
- Human Review Minutes；
- Rework Cycles；
- Token/Compute/CI Cost；
- Time to First Useful PR；
- Production Escapes。

## 五、不要只用通过率

测试可能被错误修改；隐藏测试可能不完整；代码可通过但不可维护。增加人工 Rubric：业务正确、边界、可读性、测试质量、安全、运行、文档。

## 六、对照实验

```text
A：新人 + 通用 Agent
B：新人 + Rules
C：新人 + Rules + Golden Path
D：新人 + Rules + Golden Path + MCP
```

使用同任务、相近能力、记录时间和 Review。避免只比较不同难度项目。

## 七、Eval Case

```yaml
id: ORDER-CONCURRENCY-001
prompt: 实现库存扣减
visibleAcceptance: 库存不足返回冲突
hiddenChecks:
  - 20 concurrent requests, stock=1, success<=1
  - stock never negative
  - transaction consistent
forbidden:
  - JVM local lock as only protection
scoring:
  correctness: 40
  tests: 20
  architecture: 15
  security: 10
  observability: 5
  maintainability: 10
```

## 八、回归

Rules/MCP/模型版本变化都跑固定 Eval；按 Task Category 和风险分层分析。新事故加入 Eval。

## 九、数据污染

Eval Prompt/隐藏答案不要进入 Agent 可检索知识库；生产历史内容脱敏；记录模型、参数、工具版本和随机性。

## 十、组织指标

不以代码行数评价。看 Lead Time、Review、缺陷、恢复、认知负担和新人达到独立交付的时间。
