import decimal

import tooltable  # type: ignore
import toolstr

from ctc.toolbox import validate_utils

from . import uniswap_spec


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
        fee_rate = uniswap_spec.default_trade_fee
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
        fee_rate = uniswap_spec.default_trade_fee
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
        fee_rate = uniswap_spec.default_trade_fee
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
        fee_rate = uniswap_spec.default_trade_fee
    validate_utils._ensure_non_negative(y_bought)
    beta = y_bought / y_reserves
    gamma = 1 - fee_rate
    x_sold = beta / (1 - beta) / gamma * x_reserves
    return x_sold


#
# # summary functions
#


def report_trade_summary(
    x_name=None,
    y_name=None,
    x_holdings_before=None,
    y_holdings_before=None,
    indent=None,
    **trade_kwargs
):

    if x_name is None:
        x_name = 'X'
    if y_name is None:
        y_name = 'Y'

    trade_summary = summarize_trade(**trade_kwargs)

    x_sold = trade_summary['trade_results']['x_sold']
    y_sold = trade_summary['trade_results']['y_sold']

    indent = toolstr.indent_to_str(indent=indent)

    if x_sold == 0:
        print(indent + 'trade size of 0')
    elif x_sold > 0:
        print(indent + '-', x_name, 'sold:', toolstr.format(x_sold))
        print(indent + '-', y_name, 'bought:', toolstr.format(-y_sold))
        fees = trade_summary['x_fees']
        print(indent + '- fees:', toolstr.format(fees), x_name)
    else:
        print(indent + '-', x_name, 'bought:', toolstr.format(-x_sold))
        print(indent + '-', y_name, 'sold:', toolstr.format(y_sold))
        fees = trade_summary['y_fees']
        print(indent + '- fees:', toolstr.format(fees), y_name)
    print(indent + '- prices:')
    headers = [
        '',
        'P_mean',
        'P_start',
        'P_end',
        'mean slippage',
        'end slippage',
    ]
    rows = []
    row = [
        x_name + ' / ' + y_name,
        toolstr.format(trade_summary['mean_x_per_y']),
        toolstr.format(trade_summary['x_per_y_start']),
        toolstr.format(trade_summary['x_per_y_end']),
        toolstr.format(trade_summary['mean_slippage_x_per_y']),
        toolstr.format(trade_summary['end_slippage_x_per_y']),
    ]
    rows.append(row)
    row = [
        y_name + ' / ' + x_name,
        toolstr.format(trade_summary['mean_y_per_x']),
        toolstr.format(trade_summary['y_per_x_start']),
        toolstr.format(trade_summary['y_per_x_end']),
        toolstr.format(trade_summary['mean_slippage_y_per_x']),
        toolstr.format(trade_summary['end_slippage_y_per_x']),
    ]
    rows.append(row)
    print()
    tooltable.print_table(
        rows=rows, headers=headers, indent='    ' + indent, column_gap_spaces=1
    )

    print()
    print(indent + '- pool reserve sizes:')
    print()
    headers = ['', 'before', 'after', 'change']
    new_x_reserves = trade_summary['trade_results']['new_pool']['x_reserves']
    new_y_reserves = trade_summary['trade_results']['new_pool']['y_reserves']
    x_change = new_x_reserves / trade_kwargs['x_reserves'] - 1
    y_change = new_y_reserves / trade_kwargs['y_reserves'] - 1
    rows = [
        [
            x_name,
            toolstr.format(trade_kwargs['x_reserves']),
            toolstr.format(new_x_reserves),
            toolstr.format(x_change),
        ],
        [
            y_name,
            toolstr.format(trade_kwargs['y_reserves']),
            toolstr.format(new_y_reserves),
            toolstr.format(y_change),
        ],
    ]
    tooltable.print_table(
        rows=rows,
        headers=headers,
        indent='    ' + indent,
        column_gap_spaces=1,
        decimal_places=2,
    )


def summarize_trade(**trade_kwargs):
    """compute y_bought and new pool values when trading x_sold"""

    # compute trade
    results = trade(**trade_kwargs)

    # compute mean price
    mean_x_per_y = results['x_sold'] / results['y_bought']
    mean_y_per_x = 1 / mean_x_per_y

    # compute slippage
    x_per_y_start = trade_kwargs['x_reserves'] / trade_kwargs['y_reserves']
    y_per_x_start = 1 / x_per_y_start
    x_per_y_end = (
        results['new_pool']['x_reserves'] / results['new_pool']['y_reserves']
    )
    y_per_x_end = 1 / x_per_y_end
    end_slippage_x_per_y = x_per_y_end / x_per_y_start - 1
    end_slippage_y_per_x = y_per_x_end / y_per_x_start - 1
    mean_slippage_x_per_y = mean_x_per_y / x_per_y_start - 1
    mean_slippage_y_per_x = mean_y_per_x / y_per_x_start - 1

    # compute fees
    if trade_kwargs.get('fee_rate') is None:
        trade_kwargs['fee_rate'] = uniswap_spec.default_trade_fee
    if results['x_sold'] > 0:
        x_fees = results['x_sold'] * trade_kwargs['fee_rate']
        y_fees = 0
    else:
        y_fees = results['y_sold'] * trade_kwargs['fee_rate']
        x_fees = 0

    return {
        'end_slippage_x_per_y': end_slippage_x_per_y,
        'end_slippage_y_per_x': end_slippage_y_per_x,
        'mean_slippage_x_per_y': mean_slippage_x_per_y,
        'mean_slippage_y_per_x': mean_slippage_y_per_x,
        'mean_x_per_y': mean_x_per_y,
        'mean_y_per_x': mean_y_per_x,
        'x_per_y_start': x_per_y_start,
        'y_per_x_start': y_per_x_start,
        'x_per_y_end': x_per_y_end,
        'y_per_x_end': y_per_x_end,
        'x_fees': x_fees,
        'y_fees': y_fees,
        'trade_results': results,
    }

