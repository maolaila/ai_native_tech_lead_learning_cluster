package com.example.minicommerce.notification.api;

import com.example.minicommerce.notification.application.NotificationQueryService;
import com.example.minicommerce.notification.application.NotificationQueryService.NotificationView;
import com.example.minicommerce.shared.security.CurrentUser;
import java.util.List;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

/**
 * 通知模块的 HTTP/API 适配层。
 *
 * <p><strong>作用：</strong>从安全上下文取得当前用户，并调用通知应用服务返回该用户自己的通知列表。
 *
 * <p><strong>为什么不直接访问 Repository：</strong>Controller 属于 HTTP 边界，Repository 属于数据库适配器。 直接依赖会让 API 泄露
 * JPA Entity 和查询细节，也使权限、映射和事务逻辑散落在传输层；本项目通过 ArchUnit 自动阻止这种跨层依赖。
 *
 * <p><strong>对应文档：</strong> {@code 02_backend_spring/02_Controller_Service_Repository分层.md}、 {@code
 * 05_auth_security/02_RBAC与对象级权限.md}、 {@code 11_system_design/02_模块化单体与边界.md}。
 */
@RestController
@RequestMapping("/api/notifications")
public class NotificationController {

    private final NotificationQueryService queryService;
    private final CurrentUser currentUser;

    public NotificationController(NotificationQueryService queryService, CurrentUser currentUser) {
        this.queryService = queryService;
        this.currentUser = currentUser;
    }

    /** 查询当前用户的通知。用户 ID 不从 Query 参数接收，避免普通用户通过替换 ID 查询他人通知。 */
    @GetMapping
    public List<NotificationView> list() {
        return queryService.listForUser(currentUser.require().id());
    }
}
