# 数据库 Migration 与应用发布顺序

> **所属模块：** 09 CI/CD
> **本文用途：** 避免应用和 Schema 在滚动发布、回滚和大表变更时不兼容。
> **前置知识：** 数据库 Migration
> **建议投入：** 阅读 4 小时，演练 6 小时

---

## 一、为什么特别危险

应用可快速替换；数据库是共享、有状态、可能不可逆。滚动发布时新旧实例会同时运行，Schema 必须与两者兼容。

## 二、错误案例

一次发布：Rename `customer_name` → `buyer_name`，同时新代码只读新列。旧实例仍读旧列，会立即失败；应用回滚也失败，因为旧列已没了。

## 三、Expand-Contract

### Release A：Expand

- 加 `buyer_name` 可空；
- 新代码读新列，缺失时回退旧列；
- 写时双写；
- 发布新旧兼容代码。

### Backfill

分批回填、限速、可暂停、监控锁和延迟。

### Release B

切换只读新列，停止旧写，观察。

### Release C：Contract

确认无旧实例、无旧读写、备份后删除旧列。

## 四、谁执行 Migration

选择：独立 Migration Job、发布前步骤、单实例启动任务。不要让 20 个实例同时跑同一个大 Migration。

## 五、失败

Migration 必须有 Lock Timeout、Statement Timeout、日志、停止条件和人工介入方式。不要失败后盲目无限重试 DDL。

## 六、Rollback 与 Forward Fix

可逆小变更可 Down Migration；大数据变更/删列通常偏向兼容性前滚修复。关键是发布前保留兼容窗口。

## 七、CI 验证

- 空库执行全部 Migration；
- 旧 Schema 升级；
- 新旧应用兼容测试；
- 约束和索引；
- 大表 Migration 风险静态/人工审查；
- 备份恢复验证。

## 八、Checklist

变更大小、锁级别、预计时长、滚动兼容、回滚应用、数据回填、索引创建方式、可观察指标、Owner、停止条件。
