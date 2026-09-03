# Runbook：订单错误率升高

确认范围和版本；暂停发布；必要时关闭 Feature Flag/限流；保存 Dashboard、Trace、Log、DB 状态；检查库存冲突、连接池等待、慢 SQL、Redis 回源和支付超时；回滚同一镜像 Digest；执行 Smoke 与数据一致性查询；建立时间线并把结论转为测试、告警或规则。
