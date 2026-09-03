package com.example.minicommerce.shared.domain;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.util.Objects;

/**
 * 金额值对象：禁止 double，且把币种和舍入规则放在同一语义对象中。
 * 对应文档：02_backend_spring/03_DTO_Entity_Domain与映射.md、04_database_postgresql/02_约束_范式与数据建模.md。
 */
public record Money(BigDecimal amount, String currency) {
    public Money {
        Objects.requireNonNull(amount, "amount");
        Objects.requireNonNull(currency, "currency");
        if (currency.length() != 3) throw new IllegalArgumentException("currency 必须是三位代码");
        amount = amount.setScale(2, RoundingMode.HALF_UP);
    }

    public static Money zero(String currency) {
        return new Money(BigDecimal.ZERO, currency);
    }

    public Money add(Money other) {
        requireSameCurrency(other);
        return new Money(amount.add(other.amount), currency);
    }

    public Money subtract(Money other) {
        requireSameCurrency(other);
        return new Money(amount.subtract(other.amount), currency);
    }

    public Money multiply(int quantity) {
        if (quantity <= 0) throw new IllegalArgumentException("quantity 必须大于 0");
        return new Money(amount.multiply(BigDecimal.valueOf(quantity)), currency);
    }

    private void requireSameCurrency(Money other) {
        if (!currency.equals(other.currency)) throw new IllegalArgumentException("币种不一致");
    }
}
