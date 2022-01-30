import decimal

from ctc.toolbox import validate_utils


def trade(
    x_reserves,
    y_reserves,
    x_sold=None,
    x_bought=None,
    y_sold=None,
    y_bought=None,
    new_x_reserves=None,
    new_y_reserves=None,
    fee_rate=None,
):
    """perform trade with AMM

    ## Input Requirements
    - all input values must be positive
    - must always specify both x_reserves and y_reserves
    - must specify exactly one of:
        - x_sold
        - x_bought
        - y_sold
        - y_bought
        - new_x_reserves
        - new_y_reserves
    - values in this list can be scalars or numpy arrays

    ## Inputs
    - [see uniswap_spec.py]
    """

    # validate inputs
    if fee_rate is None:
        fee_rate = 0.003
    value = validate_utils._ensure_exactly_one(
        x_sold, x_bought, y_sold, y_bought, new_x_reserves, new_y_reserves
    )
    validate_utils._ensure_non_negative(value)

    kwargs = {
        'x_reserves': x_reserves,
        'y_reserves': y_reserves,
        'fee_rate': fee_rate,
    }
    reverse_kwargs = {
        'y_reserves': x_reserves,
        'x_reserves': y_reserves,
        'fee_rate': fee_rate,
    }

    if x_sold is not None:

        # case: sell x for y, x specified
        x_bought = -x_sold
        y_bought = compute_y_bought_when_x_sold(x_sold=x_sold, **kwargs)
        y_sold = -y_bought

    elif y_sold is not None:

        # case: sell y for x, y specified
        y_bought = -y_sold
        x_bought = compute_y_bought_when_x_sold(x_sold=y_sold, **reverse_kwargs)
        x_sold = -x_bought

    elif x_bought is not None:

        # case: sell y for x, x specified
        x_sold = -x_bought
        y_sold = compute_x_sold_when_y_bought(
            y_bought=x_bought, **reverse_kwargs
        )
        y_bought = -y_sold

    elif y_bought is not None:

        # case: sell y for x, x specified
        y_sold = -y_bought
        x_sold = compute_x_sold_when_y_bought(y_bought=y_bought, **kwargs)
        x_bought = -x_sold

    else:
        raise Exception('could not compute output')

    return {
        'x_bought': x_bought,
        'x_sold': x_sold,
        'y_bought': y_bought,
        'y_sold': y_sold,
        'fee_rate': fee_rate,
        'new_pool': {
            'x_reserves': x_reserves + x_sold,
            'y_reserves': y_reserves + y_sold,
        },
    }


def trade_to_target_reserves(
    x_reserves,
    y_reserves,
    new_x_reserves=None,
    new_y_reserves=None,
    fee_rate=None,
):
    """compute trade required to reach specific target token reserve amounts"""

    kwargs = {
        'x_reserves': x_reserves,
        'y_reserves': y_reserves,
        'fee_rate': fee_rate,
    }

    # convert reserve targets to bought or sold amounts
    if new_x_reserves is not None:
        if validate_utils._ensure_positive(
            x_reserves - new_x_reserves, error=False
        ):
            x_bought = x_reserves - new_x_reserves
            return trade(x_bought=x_bought, **kwargs)
        else:
            x_sold = new_x_reserves - x_reserves
            return trade(x_sold=x_sold, **kwargs)
    elif new_y_reserves is not None:
        if validate_utils._ensure_positive(
            y_reserves - new_y_reserves, error=False
        ):
            y_bought = y_reserves - new_y_reserves
            return trade(y_bought=y_bought, **kwargs)
        else:
            y_sold = new_y_reserves - y_reserves
            return trade(y_sold=y_sold, **kwargs)
    else:
        raise Exception('specify either new_x_reserves or new_y_reserves')


def trade_to_price(
    x_reserves,
    y_reserves,
    new_x_per_y=None,
    new_y_per_x=None,
    fee_rate=None,
):
    """compute trade required to reach specific price"""

    kwargs = {
        'x_reserves': x_reserves,
        'y_reserves': y_reserves,
        'fee_rate': fee_rate,
    }
    reverse_kwargs = {
        'x_reserves': y_reserves,
        'y_reserves': x_reserves,
        'fee_rate': fee_rate,
    }

    validate_utils._ensure_exactly_one(new_x_per_y, new_y_per_x)

    # convert prices to x per y
    if new_y_per_x is not None:
        new_x_per_y = new_y_per_x ** -1

    # compute trades
    if new_x_per_y >= x_reserves / y_reserves:
        # case: sell x to increase x per y
        x_sold = compute_x_sold_to_reach_price(
            new_x_per_y=new_x_per_y, **kwargs
        )
        return trade(x_sold=x_sold, **kwargs)
    else:
        # case: sell y to decrease x per y
        y_sold = compute_x_sold_to_reach_price(
            new_x_per_y=(new_x_per_y ** -1), **reverse_kwargs
        )
        return trade(y_sold=y_sold, **kwargs)


def compute_x_sold_to_reach_price(
    x_reserves,
    y_reserves,
    new_x_per_y,
    fee_rate=None,
):
    """use quadratic formula to find trade size needed to reach new price

    - see wolframalpha.com/input/?i=g+x%5E2+%2B+%281+%2B+g%29+x+%2B+C+%3D+0
    """
    if fee_rate is None:
        fee_rate = 0.003
    gamma = 1 - fee_rate
    C = 1 - new_x_per_y * y_reserves / x_reserves
    alpha = (gamma + 1) ** 2 - 4 * C * gamma
    if isinstance(gamma, decimal.Decimal):
        alpha = alpha.sqrt()
    else:
        alpha = alpha ** 0.5
    alpha = alpha - gamma - 1
    alpha = alpha / 2 / gamma
    x_sold = alpha * x_reserves
    return x_sold


def compute_y_bought_when_x_sold(x_sold, x_reserves, y_reserves, fee_rate=None):
    """compute amount of y bought when selling x_sold amount of x"""
    if fee_rate is None:
        fee_rate = 0.003
    validate_utils._ensure_non_negative(x_sold)
    alpha = x_sold / x_reserves
    gamma = 1 - fee_rate
    y_bought = alpha * gamma / (1 + alpha * gamma) * y_reserves
    return y_bought


def compute_x_sold_when_y_bought(
    y_bought,
    x_reserves,
    y_reserves,
    fee_rate=None,
):
    """compute amount of x that must be sold to buy y_bought amount of y"""
    if fee_rate is None:
        fee_rate = 0.003
    validate_utils._ensure_non_negative(y_bought)
    beta = y_bought / y_reserves
    gamma = 1 - fee_rate
    x_sold = beta / (1 - beta) / gamma * x_reserves
    return x_sold

