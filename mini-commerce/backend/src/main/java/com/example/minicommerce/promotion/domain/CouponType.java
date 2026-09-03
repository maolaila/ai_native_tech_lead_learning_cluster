package com.example.minicommerce.promotion.domain;

/**
 * 优惠券模块的领域模型层：{@code CouponType}。
 *
 * <p><strong>作用：</strong>表达业务状态、行为和不变量，并尽量保持对 Spring、HTTP 与数据库实现无感。
 *
 * <p><strong>为什么：</strong>领域方法比任意 Setter 更能阻止非法状态，也使测试直接描述业务语言。
 *
 * <p><strong>对应文档：</strong> {@code 03_testing/02_测试用例设计.md}、 {@code
 * 04_database_postgresql/02_约束_范式与数据建模.md}。
 */
public enum CouponType {
    PERCENT,
    FIXED
}
