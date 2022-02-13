import toolstr
import tooltable  # type: ignore

from . import cpmm_trade


def print_pool_summary(
    x_reserves,
    y_reserves,
    lp_total_supply=None,
    x_name=None,
    y_name=None,
    fee_rate=None,
    indent=None,
    depths=None,
):
    # add in +/- 2% depth

    if x_name is None:
        x_name = 'X'
    if y_name is None:
        y_name = 'Y'

    indent = toolstr.indent_to_str(indent)

    print(indent + '- ' + x_name + ' reserves:', toolstr.format(x_reserves, order_of_magnitude=True))
    print(indent + '- ' + y_name + ' reserves:', toolstr.format(y_reserves, order_of_magnitude=True))
    if lp_total_supply is not None:
        print(indent + '- total lp tokens:', toolstr.format(lp_total_supply, order_of_magnitude=True))
    print(
        indent + '-',
        x_name,
        '/',
        y_name + ' price:',
        # '%.6f' % (x_reserves / y_reserves),
        toolstr.format(x_reserves / y_reserves),
    )
    print(
        indent + '-',
        y_name,
        '/',
        x_name + ' price:',
        # '%.6f' % (y_reserves / x_reserves),
        toolstr.format(y_reserves / x_reserves),
    )
    print(indent + '-', x_name + ' / ' + y_name, 'liquidity depth:')
    print()
    print_liquidity_depth(
        x_reserves=x_reserves,
        y_reserves=y_reserves,
        x_name=x_name,
        y_name=y_name,
        fee_rate=fee_rate,
        indent=indent,
        depths=depths,
    )
    print()
    print(indent + '-', y_name + ' / ' + x_name, 'liquidity depth:')
    print()
    print_liquidity_depth(
        x_reserves=y_reserves,
        y_reserves=x_reserves,
        x_name=y_name,
        y_name=x_name,
        fee_rate=fee_rate,
        indent=indent,
        depths=depths,
    )
    print()


def print_liquidity_depth(
    x_reserves,
    y_reserves,
    depths=None,
    x_name=None,
    y_name=None,
    fee_rate=None,
    indent=None,
):

    if x_name is None:
        x_name = 'X'
    if y_name is None:
        y_name = 'Y'

    if depths is None:
        depths = [-0.10, -0.05, -0.02, 0, 0.02, 0.05, 0.10]

    format_str = '{:,.2f}'

    current_x_per_y = x_reserves / y_reserves
    headers = ['depth', 'new price', x_name, y_name]

    trades = []
    for depth in depths:

        trade = []

        # x per y
        if depth == 0:
            trade.append(' 0%')
        else:
            trade.append('%+.0f' % (depth * 100) + '%')

        # new price
        new_x_per_y = type(current_x_per_y)(1 + depth) * current_x_per_y
        trade.append(toolstr.format(new_x_per_y))
        trade[-1] = trade[-1] + ' ' + x_name + ' / ' + y_name

        # buys and sells
        result = cpmm_trade.trade_to_price(
            x_reserves=x_reserves,
            y_reserves=y_reserves,
            new_x_per_y=new_x_per_y,
            fee_rate=fee_rate,
        )
        if depth != 0 and result['x_sold'] > 0:
            trade.append('sell ' + toolstr.format(result['x_sold'], order_of_magnitude=True))
            trade.append(' buy ' + toolstr.format(result['y_bought'], order_of_magnitude=True))
        elif depth != 0 and result['x_sold'] < 0:
            trade.append(' buy ' + toolstr.format(result['x_bought'], order_of_magnitude=True))
            trade.append('sell ' + toolstr.format(result['y_sold'], order_of_magnitude=True))
        else:
            trade.append('     0.00')
            trade.append('     0.00')
        trades.append(trade)

    indent = ' ' * 4 + toolstr.indent_to_str(indent)
    tooltable.print_table(rows=trades, headers=headers, indent=indent)


def print_trade_summary(
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
    results = cpmm_trade.trade(**trade_kwargs)

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

