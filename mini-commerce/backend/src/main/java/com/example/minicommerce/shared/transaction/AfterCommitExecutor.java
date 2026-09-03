package com.example.minicommerce.shared.transaction;

import org.springframework.stereotype.Component;
import org.springframework.transaction.support.TransactionSynchronization;
import org.springframework.transaction.support.TransactionSynchronizationManager;

/**
 * 仅把可重试/可补偿的非核心动作放到提交后。关键可靠异步动作仍需 Outbox，不能只依赖 afterCommit 回调。
 */
@Component
public class AfterCommitExecutor {
    public void run(Runnable action) {
        if (!TransactionSynchronizationManager.isActualTransactionActive()) { action.run(); return; }
        TransactionSynchronizationManager.registerSynchronization(new TransactionSynchronization() {
            @Override public void afterCommit() { action.run(); }
        });
    }
}
