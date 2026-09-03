package com.example.minicommerce.notification.application;

import com.example.minicommerce.notification.infrastructure.NotificationEntity;
import com.example.minicommerce.notification.infrastructure.NotificationRepository;
import java.time.Instant;
import java.util.List;
import java.util.UUID;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

/**
 * 通知模块的只读应用服务。
 *
 * <p><strong>作用：</strong>按当前用户查询最近通知，并把持久化实体映射成稳定的应用层读取模型。 API 层因此不需要知道 JPA Entity、Repository
 * 方法名或表结构。
 *
 * <p><strong>为什么增加这一层：</strong>Controller 直接访问 Repository 会把 HTTP 与数据库结构耦合在一起，
 * 也违反项目的模块分层规则。查询即使简单，也应该通过公开的应用能力暴露；以后增加已读过滤、分页或脱敏时， 不需要改动 Controller 与持久化边界之间的依赖方向。
 *
 * <p><strong>对应文档：</strong> {@code 02_backend_spring/02_Controller_Service_Repository分层.md}、 {@code
 * 02_backend_spring/03_DTO_Entity_Domain与映射.md}、 {@code 11_system_design/02_模块化单体与边界.md}。
 */
@Service
@Transactional(readOnly = true)
public class NotificationQueryService {

    private final NotificationRepository repository;

    public NotificationQueryService(NotificationRepository repository) {
        this.repository = repository;
    }

    /** 查询某个用户最近 50 条通知；用户 ID 必须来自经过认证的服务端主体。 */
    public List<NotificationView> listForUser(Long userId) {
        return repository.findTop50ByUserIdOrderByCreatedAtDesc(userId).stream()
                .map(NotificationQueryService::toView)
                .toList();
    }

    private static NotificationView toView(NotificationEntity notification) {
        return new NotificationView(
                notification.getId(),
                notification.getMessage(),
                notification.isUnread(),
                notification.getCreatedAt());
    }

    /** API 可安全返回的通知读取模型，不暴露 Entity 的内部持久化状态。 */
    public record NotificationView(UUID id, String message, boolean unread, Instant createdAt) {}
}
