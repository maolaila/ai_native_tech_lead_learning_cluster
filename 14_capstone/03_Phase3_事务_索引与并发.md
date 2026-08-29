# Phase 3：事务、索引、锁与并发

> **所属模块：** 14 Capstone
> **本文用途：** 让订单在真实数据量和并发下保持正确，并建立数据库诊断能力。
> **前置知识：** Phase 2、数据库模块
> **建议投入：** 5～7 周

---

## 数据量

生成 100 万 orders 和数百万 order_items，记录脚本、耗时、磁盘和统计。

## Index

用户最近订单、状态后台查询、未支付过期订单；比较无索引、单列、复合、Partial 和错误顺序。

## Transaction

订单、Item、库存、幂等记录同事务；在每一步故意失败，证明无半成功。

## Concurrency

stock=1、20/100 并发：先复现超卖，再实现条件 UPDATE；比较悲观/乐观方案和延迟。

## Deadlock

多商品反序锁定复现；固定顺序；有限重试；记录 SQL 和线程。

## Connection Pool

Pool=2、长事务/慢 SQL，观察 Pending 和 Timeout；修根因。

## Migration

完成一次 Expand-Contract，旧/新应用兼容测试。

## Backup

备份→删除 Volume→恢复→跑 Smoke/一致性检查，记录 RTO。

## 输出

数据库设计文档、索引报告、并发报告、Migration Checklist、Restore Runbook、相关 ADR。
