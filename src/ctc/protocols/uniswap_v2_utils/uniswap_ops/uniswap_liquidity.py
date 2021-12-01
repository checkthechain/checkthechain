import decimal

import numpy as np

from ctc.toolbox import validate_utils


def mint_liquidity(
    x_reserves,
    y_reserves,
    lp_total_supply,
    x_deposited=None,
    y_deposited=None,
    lp_minted=None,
):

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
    if not isinstance(alpha, decimal.Decimal) and np.isinf(alpha):
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
    x_reserves,
    y_reserves,
    lp_total_supply,
    x_withdrawn=None,
    y_withdrawn=None,
    lp_burned=None,
):

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

