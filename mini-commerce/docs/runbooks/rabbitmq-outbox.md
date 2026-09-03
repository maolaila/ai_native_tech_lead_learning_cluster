# Runbook：RabbitMQ 不可用与 Outbox 积压

1. 确认订单事务仍成功、Outbox PENDING/FAILED 增长，避免误判为订单丢失。
2. 检查 Broker 健康、DNS、端口、权限、Exchange 和 Confirm。
3. 查看最老事件、attempt_count、last_error；不要直接清表。
4. 恢复 Broker 后观察 Publisher 追平速度与 Consumer/DLQ。
5. 重放前确认消费者幂等、Schema 兼容、速率、停止条件和审批。
6. 验证通知/积分与订单数据，不只看 Queue 归零。
