# Incident 响应与生产 Debug 流程

> **所属模块：** 10 Observability
> **本文用途：** 建立止血、定位、恢复、沟通和无责复盘闭环。
> **前置知识：** Logs/Metrics/Traces
> **建议投入：** 阅读 4 小时，演练 5 小时

---

## 一、目标顺序

```text
确认用户影响
→ 指定 Incident Commander
→ 止血
→ 保留证据
→ 定位
→ 恢复
→ 验证
→ 复盘和系统改进
```

生产事故中先降低影响，不必先找到完美根因。

## 二、角色

Incident Commander 协调；Operations 执行动作；Communications 更新利益相关者；Subject Experts 调查。小团队可一人多角色，但职责要明确。

## 三、止血

回滚、关闭 Feature Flag、降级非核心、限流、隔离坏实例、暂停 Consumer、阻止坏写。每个动作要考虑数据和副作用。

## 四、调查顺序

1. 时间、版本、范围、业务影响；
2. RED 和 SLO；
3. Deploy/Config/Migration；
4. Trace 定位慢/错的 Span；
5. Logs 查上下文；
6. DB Locks/Pool/Slow Query；
7. Redis/MQ/External；
8. 数据一致性。

## 五、不要破坏证据

不要第一时间重启全部、清 Queue、删 Pod、改多处配置。先保存时间线、Dashboard、Log/Trace、版本、配置差异和数据样本。

## 六、时间线

```text
14:02 发布 v1.8
14:05 P99 上升
14:07 订单错误 8%
14:09 暂停发布
14:12 Canary 回滚
14:16 恢复
```

事实和假设分开。

## 七、复盘

无责不等于无责任。关注系统为何允许错误达到用户：测试缺口、门禁、监控、权限、复杂流程、文档、压力。

输出：影响、检测、根因、促成因素、哪些机制有效/失效、修复项、Owner、截止时间。

## 八、避免“人为失误”作为终点

继续问：为什么单人可执行危险操作？为什么无预览/审批？为什么回滚没演练？为什么错误不可观测？

## 九、每个事故至少沉淀

Regression Test、Alert/Dashboard、Runbook、Guardrail/权限、架构或流程改进之一，最好多个。
