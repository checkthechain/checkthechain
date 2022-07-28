from __future__ import annotations

from ctc import spec


def get_stableswap_price(
    x: spec.Number, y: spec.Number, *, A: spec.Number
) -> float:
    k = x + y
    numerator = 1 + 2 * A * (x ** 2) * y / ((k / 2) ** 3)
    denominator = 1 + 2 * A * x * (y ** 2) / ((k / 2) ** 3)
    return float(y / x * numerator / denominator)
