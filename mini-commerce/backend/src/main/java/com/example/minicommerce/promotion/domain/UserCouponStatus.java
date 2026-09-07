package com.example.minicommerce.promotion.domain;

/**
 * 个人优惠券的状态：已发放、已占用、已使用、已过期。
 *
 * <p><strong>作用：</strong>个人优惠券的状态：已发放、已占用、已使用、已过期。
 *
 * <p><strong>为什么：</strong>状态列表并不代表自动运行过期任务；本项目主要在使用时检查有效期。
 *
 * <p><strong>对应文档：</strong> {@code 03_testing/02_测试用例设计.md}、 {@code
 * 04_database_postgresql/02_约束_范式与数据建模.md}。
 */
public enum UserCouponStatus {
    ISSUED,
    RESERVED,
    USED,
    EXPIRED
}
