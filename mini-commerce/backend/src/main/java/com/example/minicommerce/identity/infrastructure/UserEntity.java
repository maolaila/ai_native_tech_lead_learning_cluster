package com.example.minicommerce.identity.infrastructure;

import com.example.minicommerce.identity.domain.UserRole;
import com.example.minicommerce.shared.persistence.BaseEntity;
import jakarta.persistence.*;

/**
 * 持久化实体不直接作为 API Response，避免 passwordHash 等内部字段因序列化配置变化而泄露。
 * 对应文档：02_backend_spring/03_DTO_Entity_Domain与映射.md。
 */
@Entity
@Table(name = "app_users", uniqueConstraints = @UniqueConstraint(name = "ux_users_email", columnNames = "email"))
public class UserEntity extends BaseEntity {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    @Column(nullable = false, length = 320)
    private String email;
    @Column(name = "display_name", nullable = false, length = 100)
    private String displayName;
    @Column(name = "password_hash", nullable = false, length = 100)
    private String passwordHash;
    @Enumerated(EnumType.STRING) @Column(nullable = false, length = 20)
    private UserRole role;
    @Column(nullable = false)
    private boolean enabled = true;

    protected UserEntity() {}
    public UserEntity(String email, String displayName, String passwordHash, UserRole role) {
        this.email = email.toLowerCase(); this.displayName = displayName; this.passwordHash = passwordHash; this.role = role;
    }
    public Long getId() { return id; }
    public String getEmail() { return email; }
    public String getDisplayName() { return displayName; }
    public String getPasswordHash() { return passwordHash; }
    public UserRole getRole() { return role; }
    public boolean isEnabled() { return enabled; }
    public void disable() { enabled = false; }
}
