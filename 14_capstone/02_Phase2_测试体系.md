# Phase 2：分层自动化测试

> **所属模块：** 14 Capstone
> **本文用途：** 把人工点击升级为可重复验证和 CI 基础。
> **前置知识：** Phase 1、测试模块
> **建议投入：** 4～5 周

---

## Unit

Order/Money/Status/Discount/Permission Policy；正常、边界、异常；固定 Clock；无 Spring。

## Frontend

Cart Store、表单、Error Code、重复提交、Loading/Error/Empty、权限可见性。

## Integration

Testcontainers PostgreSQL；真实 Flyway；Repository Mapping；Unique/FK/Check；订单事务回滚。

## API

Method/Path/Status/Schema/Validation/Authentication/Authorization/Error/Idempotency。

## E2E

登录、商品、下单、订单、Admin；库存不足、500、越权；无固定 Sleep；Trace/Screenshot。

## Regression

故意制造 5 个 Bug：金额边界、状态机、DTO 泄露、事务、前端重复提交。先失败测试再修复。

## Test Strategy

说明每层职责、数据隔离、Fixture、Suite、Flaky、Coverage、CI 运行时机。

## 验收

完整套件一键执行；连续 10 次稳定；每个核心不变量至少有自动验证；AI 生成测试经过人工 Review。
