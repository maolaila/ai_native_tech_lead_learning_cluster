package com.example.minicommerce.shared.domain;

import static org.assertj.core.api.Assertions.*;

import java.math.BigDecimal;
import org.junit.jupiter.api.Test;

/**
 * 共享技术基础模块的自动化验证层：{@code MoneyTest}。
 *
 * <p><strong>作用：</strong>提供可重复的行为、数据、并发或故障证据，而不是只证明代码能够编译。
 *
 * <p><strong>为什么：</strong>历史规则和 Bug 只有进入自动化测试，才不会在后续重构或 AI 生成代码时悄悄回归。
 *
 * <p><strong>对应文档：</strong> {@code 02_backend_spring/01_请求生命周期与IoC_DI.md}、 {@code
 * 02_backend_spring/04_API设计_校验_异常与错误码.md}、 {@code 11_system_design/02_模块化单体与边界.md}。
 */
class MoneyTest {
    @Test
    void add_requiresSameCurrency() {
        assertThatThrownBy(
                        () ->
                                new Money(new BigDecimal("1"), "JPY")
                                        .add(new Money(new BigDecimal("1"), "USD")))
                .isInstanceOf(IllegalArgumentException.class);
    }

    @Test
    void multiply_usesDecimalMoney() {
        assertThat(new Money(new BigDecimal("8.00"), "JPY").multiply(3).amount())
                .isEqualByComparingTo("24.00");
    }
}
