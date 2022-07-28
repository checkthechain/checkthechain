from __future__ import annotations

import decimal
import math

from ctc.toolbox import validate_utils
from . import cpmm_spec


def mint_liquidity(
    x_reserves: int | float,
    y_reserves: int | float,
    *,
    lp_total_supply: int | float,
    x_deposited: int | float | None = None,
    y_deposited: int | float | None = None,
    lp_minted: int | float | None = None,
) -> cpmm_spec.Mint:

    # validate inputs
    validate_utils._ensure_exactly_one(x_deposited, y_deposited, lp_minted)

    # compute alpha
    if x_deposited is not None:
        alpha = x_deposited / x_reserves
    elif y_deposited is not None:
        alpha = y_deposited / y_reserves
    elif lp_minted is not None:
        alpha = lp_minted / lp_total_supply
    else:
        raise Exception('could not compute alpha')
    if not isinstance(alpha, decimal.Decimal) and math.isinf(alpha):
        raise Exception('initialize pool first')
    elif alpha < 0:
        raise Exception('use burn_liquidity() for negative values')

    # compute new values
    x_reserves_new = (1 + alpha) * x_reserves
    y_reserves_new = (1 + alpha) * y_reserves
    lp_total_supply_new = (1 + alpha) * lp_total_supply

    return {
        'x_deposited': x_reserves_new - x_reserves,
        'y_deposited': y_reserves_new - y_reserves,
        'lp_minted': lp_total_supply_new - lp_total_supply,
        'new_pool': {
            'x_reserves': x_reserves_new,
            'y_reserves': y_reserves_new,
            'lp_total_supply': lp_total_supply_new,
        },
    }


def burn_liquidity(
    x_reserves: int | float,
    y_reserves: int | float,
    *,
    lp_total_supply: int | float,
    x_withdrawn: int | float | None = None,
    y_withdrawn: int | float | None = None,
    lp_burned: int | float | None = None,
) -> cpmm_spec.Burn:

    # validate inputs
    validate_utils._ensure_exactly_one(x_withdrawn, y_withdrawn, lp_burned)

    # compute alpha
    if x_withdrawn is not None:
        alpha = x_withdrawn / x_reserves
    elif y_withdrawn is not None:
        alpha = y_withdrawn / y_reserves
    elif lp_burned is not None:
        alpha = lp_burned / lp_total_supply
    else:
        raise Exception('could not compute alpha')
    if alpha > 1:
        raise Exception('withdrawal exceeds pool size')
    if alpha < 0:
        raise Exception('use mint_liquidity() for negative values')

    # compute new values
    x_reserves_new = (1 - alpha) * x_reserves
    y_reserves_new = (1 - alpha) * y_reserves
    lp_total_supply_new = (1 - alpha) * lp_total_supply

    return {
        'x_withdrawn': x_reserves - x_reserves_new,
        'y_withdrawn': y_reserves - y_reserves_new,
        'lp_burned': lp_total_supply - lp_total_supply_new,
        'new_pool': {
            'x_reserves': x_reserves_new,
            'y_reserves': y_reserves_new,
            'lp_total_supply': lp_total_supply_new,
        },
    }
