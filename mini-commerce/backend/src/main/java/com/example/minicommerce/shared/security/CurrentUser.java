package com.example.minicommerce.shared.security;

import com.example.minicommerce.identity.domain.UserRole;
import com.example.minicommerce.shared.error.BusinessException;
import com.example.minicommerce.shared.error.ErrorCode;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Component;

/**
 * 统一取得认证主体；业务 Service 仍必须执行对象级权限检查，不能只依赖前端隐藏按钮或 USER 角色。
 * 对应文档：05_auth_security/02_RBAC与对象级权限.md。
 */
@Component
public class CurrentUser {
    public UserPrincipal require() {
        Authentication auth = SecurityContextHolder.getContext().getAuthentication();
        if (auth == null || !(auth.getPrincipal() instanceof UserPrincipal principal)) {
            throw new BusinessException(ErrorCode.AUTHENTICATION_FAILED, "需要登录");
        }
        return principal;
    }
    public boolean isAdmin() { return require().role() == UserRole.ADMIN; }
}
