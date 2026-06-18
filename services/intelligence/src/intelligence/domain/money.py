from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from decimal import ROUND_HALF_EVEN, Decimal

CENTS = Decimal("0.01")
ROUNDING = ROUND_HALF_EVEN
DEFAULT_CURRENCY = "USD"


class CurrencyMismatchError(Exception):
    def __init__(self, left: str, right: str) -> None:
        super().__init__(f"cannot combine {left} with {right}")


@dataclass(frozen=True)
class Money:
    amount: Decimal
    currency: str = DEFAULT_CURRENCY

    @classmethod
    def of(cls, amount: Decimal | int | str | float, currency: str = DEFAULT_CURRENCY) -> Money:
        if isinstance(amount, float):
            raise TypeError("Money rejects float; pass Decimal, int, or str")
        return cls(Decimal(amount), currency)

    @classmethod
    def zero(cls, currency: str = DEFAULT_CURRENCY) -> Money:
        return cls(Decimal(0), currency)

    def _guard(self, other: Money) -> None:
        if self.currency != other.currency:
            raise CurrencyMismatchError(self.currency, other.currency)

    def __add__(self, other: Money) -> Money:
        self._guard(other)
        return Money(self.amount + other.amount, self.currency)

    def __sub__(self, other: Money) -> Money:
        self._guard(other)
        return Money(self.amount - other.amount, self.currency)

    def __mul__(self, factor: Decimal) -> Money:
        return Money(self.amount * factor, self.currency)

    def __neg__(self) -> Money:
        return Money(-self.amount, self.currency)

    def __lt__(self, other: Money) -> bool:
        self._guard(other)
        return self.amount < other.amount

    def __le__(self, other: Money) -> bool:
        self._guard(other)
        return self.amount <= other.amount

    def ratio_to(self, other: Money) -> Decimal:
        self._guard(other)
        if other.amount == 0:
            return Decimal(0)
        return self.amount / other.amount

    def quantized(self) -> Money:
        return Money(self.amount.quantize(CENTS, rounding=ROUNDING), self.currency)

    @property
    def is_zero(self) -> bool:
        return self.amount == 0

    @property
    def is_negative(self) -> bool:
        return self.amount < 0


def sum_money(items: Iterable[Money], currency: str = DEFAULT_CURRENCY) -> Money:
    total = Money.zero(currency)
    for item in items:
        total = total + item
    return total
