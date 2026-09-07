package com.example.minicommerce.promotion.domain;

/**
 * 优惠券的两种计算方式：百分比折扣和固定金额减免。
 *
 * <p><strong>作用：</strong>优惠券的两种计算方式：百分比折扣和固定金额减免。
 *
 * <p><strong>为什么：</strong>PERCENT 的 value 是百分比数值，不是直接扣除的金额；计算在 CouponService 中完成。
 *
 * <p><strong>对应文档：</strong> {@code 03_testing/02_测试用例设计.md}、 {@code
 * 04_database_postgresql/02_约束_范式与数据建模.md}。
 */
public enum CouponType {
    PERCENT,
    FIXED
}
