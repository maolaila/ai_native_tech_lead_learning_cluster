package com.example.minicommerce.shared.transaction;

import org.springframework.stereotype.Component;
import org.springframework.transaction.support.TransactionSynchronization;
import org.springframework.transaction.support.TransactionSynchronizationManager;

/**
 * 数据库确认提交成功以后，再执行一小段辅助动作，例如增加监控计数。
 *
 * <p>大白话：订单真正写好了，才在计数器上加一；事务回滚就不加。 这里不会新开线程，也不是消息队列；回调通常仍在提交事务的线程里执行。
 *
 * <p>为什么不能靠它发送关键消息：提交后如果进程突然退出，回调可能没有执行，也没有自动补发记录。 需要可靠重试的通知仍应写 Outbox。这里也不负责回滚已经提交的数据库。
 *
 * <p><strong>对应文档：</strong> {@code 02_backend_spring/01_请求生命周期与IoC_DI.md}、 {@code
 * 02_backend_spring/04_API设计_校验_异常与错误码.md}、 {@code 11_system_design/02_模块化单体与边界.md}。
 */
@Component
public class AfterCommitExecutor {
    /** action 是一段稍后执行的代码；有事务时等提交成功，没有事务时立即执行。 */
    public void run(Runnable action) {
        if (!TransactionSynchronizationManager.isActualTransactionActive()) {
            action.run();
            return;
        }
        TransactionSynchronizationManager.registerSynchronization(
                new TransactionSynchronization() {
                    @Override
                    public void afterCommit() {
                        action.run();
                    }
                });
    }
}
