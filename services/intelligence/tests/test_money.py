from __future__ import annotations

from decimal import Decimal

import pytest

from intelligence.domain.money import CurrencyMismatchError, Money, sum_money


def test_of_rejects_float() -> None:
    with pytest.raises(TypeError):
        Money.of(1.5)


def test_of_accepts_string_int_and_decimal() -> None:
    assert Money.of("10.50").amount == Decimal("10.50")
    assert Money.of(10).amount == Decimal(10)
    assert Money.of(Decimal("3.33")).amount == Decimal("3.33")


def test_addition_and_subtraction() -> None:
    assert Money.of("10") + Money.of("5") == Money.of("15")
    assert Money.of("10") - Money.of("4") == Money.of("6")


def test_combining_different_currencies_is_rejected() -> None:
    with pytest.raises(CurrencyMismatchError):
        _ = Money.of("1", "USD") + Money.of("1", "EUR")


def test_multiplication_by_a_decimal_factor() -> None:
    assert Money.of("100") * Decimal("0.25") == Money.of("25")


def test_ratio_to_zero_returns_zero_rather_than_dividing() -> None:
    assert Money.of("100").ratio_to(Money.zero()) == Decimal(0)


def test_sum_money_conserves_value() -> None:
    parts = [Money.of("33.34"), Money.of("33.33"), Money.of("33.33")]
    assert sum_money(parts) == Money.of("100.00")
