package com.example.minicommerce.shared.security;

import com.example.minicommerce.identity.domain.UserRole;
import com.example.minicommerce.identity.infrastructure.UserEntity;
import java.util.*;
import org.springframework.security.core.*;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.userdetails.UserDetails;

/**
 * 把已确认的用户 ID、邮箱和角色交给 Spring Security。
 *
 * <p><strong>作用：</strong>把已确认的用户 ID、邮箱和角色交给 Spring Security。
 *
 * <p><strong>为什么：</strong>它是当前请求的身份说明，不是数据库实体。getAuthorities 把角色转换成权限系统使用的 ROLE_ 前缀格式。
 *
 * <p><strong>对应文档：</strong> {@code 02_backend_spring/01_请求生命周期与IoC_DI.md}、 {@code
 * 02_backend_spring/04_API设计_校验_异常与错误码.md}、 {@code 11_system_design/02_模块化单体与边界.md}。
 */
public record UserPrincipal(Long id, String email, String password, UserRole role, boolean enabled)
        implements UserDetails {
    public static UserPrincipal from(UserEntity u) {
        return new UserPrincipal(
                u.getId(), u.getEmail(), u.getPasswordHash(), u.getRole(), u.isEnabled());
    }

    @Override
    public Collection<? extends GrantedAuthority> getAuthorities() {
        return List.of(new SimpleGrantedAuthority("ROLE_" + role.name()));
    }

    @Override
    public String getUsername() {
        return email;
    }

    @Override
    public String getPassword() {
        return password;
    }

    @Override
    public boolean isAccountNonExpired() {
        return true;
    }

    @Override
    public boolean isAccountNonLocked() {
        return true;
    }

    @Override
    public boolean isCredentialsNonExpired() {
        return true;
    }

    @Override
    public boolean isEnabled() {
        return enabled;
    }
}
