package com.example.minicommerce.shared.security;

import com.example.minicommerce.identity.domain.UserRole;
import com.example.minicommerce.identity.infrastructure.UserEntity;
import java.util.*;
import org.springframework.security.core.*;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.userdetails.UserDetails;

/**
 * 共享技术基础模块的安全边界层：{@code UserPrincipal}。
 *
 * <p><strong>作用：</strong>负责认证凭证解析、授权和安全策略，不把前端显示状态当成权限控制。
 *
 * <p><strong>为什么：</strong>安全必须在服务端默认拒绝，并通过角色、权限和对象所有权共同判断。
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
