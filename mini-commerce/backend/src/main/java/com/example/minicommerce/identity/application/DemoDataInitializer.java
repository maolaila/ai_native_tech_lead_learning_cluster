package com.example.minicommerce.identity.application;

import com.example.minicommerce.catalog.infrastructure.*;
import com.example.minicommerce.identity.domain.UserRole;
import com.example.minicommerce.identity.infrastructure.*;
import com.example.minicommerce.inventory.infrastructure.*;
import com.example.minicommerce.promotion.domain.CouponType;
import com.example.minicommerce.promotion.infrastructure.*;
import java.math.BigDecimal;
import java.time.*;
import java.time.temporal.ChronoUnit;
import org.springframework.boot.*;
import org.springframework.context.annotation.Profile;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Component;
import org.springframework.transaction.annotation.Transactional;

/**
 * 本地演示数据只在 local Profile 创建，生产环境绝不创建默认账号。
 *
 * <p><strong>对应文档：</strong> {@code 05_auth_security/01_Session_Cookie_Token.md}、 {@code
 * 05_auth_security/02_RBAC与对象级权限.md}、 {@code 05_auth_security/03_Web常见攻击.md}。
 */
@Component
@Profile("local")
public class DemoDataInitializer implements ApplicationRunner {
    private final UserRepository users;
    private final ProductRepository products;
    private final InventoryRepository inventory;
    private final CouponRepository coupons;
    private final UserCouponRepository userCoupons;
    private final PasswordEncoder passwords;

    public DemoDataInitializer(
            UserRepository u,
            ProductRepository p,
            InventoryRepository i,
            CouponRepository c,
            UserCouponRepository uc,
            PasswordEncoder pe) {
        users = u;
        products = p;
        inventory = i;
        coupons = c;
        userCoupons = uc;
        passwords = pe;
    }

    @Override
    @Transactional
    public void run(ApplicationArguments args) {
        UserEntity alice =
                users.findByEmailIgnoreCase("alice@example.com")
                        .orElseGet(
                                () ->
                                        users.save(
                                                new UserEntity(
                                                        "alice@example.com",
                                                        "Alice",
                                                        passwords.encode("Password123!"),
                                                        UserRole.USER)));
        users.findByEmailIgnoreCase("admin@example.com")
                .orElseGet(
                        () ->
                                users.save(
                                        new UserEntity(
                                                "admin@example.com",
                                                "Admin",
                                                passwords.encode("AdminPassword123!"),
                                                UserRole.ADMIN)));
        if (products.count() == 0) {
            ProductEntity keyboard =
                    new ProductEntity(
                            "KB-001", "机械键盘 A", "用于演示历史成交快照", new BigDecimal("8000.00"), "JPY");
            keyboard.publish();
            products.save(keyboard);
            inventory.save(new InventoryEntity(keyboard.getId(), 100));
            ProductEntity mouse =
                    new ProductEntity(
                            "MS-001", "无线鼠标", "用于并发库存实验", new BigDecimal("3200.00"), "JPY");
            mouse.publish();
            products.save(mouse);
            inventory.save(new InventoryEntity(mouse.getId(), 20));
        }
        CouponEntity coupon =
                coupons.findByCodeIgnoreCase("WELCOME10")
                        .orElseGet(
                                () ->
                                        coupons.save(
                                                new CouponEntity(
                                                        "WELCOME10",
                                                        CouponType.PERCENT,
                                                        new BigDecimal("10"),
                                                        new BigDecimal("5000"),
                                                        new BigDecimal("1000"),
                                                        Instant.now().minus(1, ChronoUnit.DAYS),
                                                        Instant.now().plus(365, ChronoUnit.DAYS))));
        userCoupons
                .findForUpdate(alice.getId(), coupon.getId())
                .orElseGet(
                        () ->
                                userCoupons.save(
                                        new UserCouponEntity(alice.getId(), coupon.getId())));
    }
}
