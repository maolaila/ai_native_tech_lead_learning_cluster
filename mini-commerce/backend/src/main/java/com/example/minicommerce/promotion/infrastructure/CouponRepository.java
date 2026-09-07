package com.example.minicommerce.promotion.infrastructure;

import java.util.Optional;
import org.springframework.data.jpa.repository.JpaRepository;

/**
 * 按券码查找优惠券模板。
 *
 * <p><strong>作用：</strong>按券码查找优惠券模板。
 *
 * <p><strong>为什么：</strong>模板查到并不代表当前用户有资格使用，还要查询个人领券记录并检查有效期和金额门槛。
 *
 * <p><strong>对应文档：</strong> {@code 03_testing/02_测试用例设计.md}、 {@code
 * 04_database_postgresql/02_约束_范式与数据建模.md}。
 */
public interface CouponRepository extends JpaRepository<CouponEntity, Long> {
    Optional<CouponEntity> findByCodeIgnoreCase(String code);
}
