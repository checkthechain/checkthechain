import toolstr
import tooltable

from . import uniswap_trades


def report_pool_summary(
    x_reserves,
    y_reserves,
    lp_total_supply=None,
    x_name=None,
    y_name=None,
    fee_rate=None,
    indent=None,
    depths=None
):
    # add in +/- 2% depth

    if x_name is None:
        x_name = 'X'
    if y_name is None:
        y_name = 'Y'

    indent = toolstr.indent_to_str(indent)

    print(indent + '- ' + x_name + ' reserves:', toolstr.format(x_reserves))
    print(indent + '- ' + y_name + ' reserves:', toolstr.format(y_reserves))
    if lp_total_supply is not None:
        print(indent + '- total lp tokens:', toolstr.format(lp_total_supply))
    print(indent + '-', x_name, '/', y_name + ' price:', '%.6f' % (x_reserves / y_reserves))
    print(indent + '-', y_name, '/', x_name + ' price:', '%.6f' % (y_reserves / x_reserves))
    print(indent + '-', x_name + ' / ' + y_name, 'liquidity depth:')
    print()
    report_liquidity_depth(
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
    report_liquidity_depth(
        x_reserves=y_reserves,
        y_reserves=x_reserves,
        x_name=y_name,
        y_name=x_name,
        fee_rate=fee_rate,
        indent=indent,
        depths=depths,
    )
    print()


def report_liquidity_depth(
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
        result = uniswap_trades.trade_to_price(
            x_reserves=x_reserves,
            y_reserves=y_reserves,
            new_x_per_y=new_x_per_y,
            fee_rate=fee_rate,
        )
        if result['x_sold'] > 0:
            trade.append('sell ' + format_str.format(result['x_sold']))
            trade.append(' buy ' + format_str.format(result['y_bought']))
        elif result['x_sold'] < 0:
            trade.append(' buy ' + format_str.format(result['x_bought']))
            trade.append('sell ' + format_str.format(result['y_sold']))
        else:
            trade.append('none 0.00')
            trade.append('none 0.00')
        trades.append(trade)

    indent = ' ' * 4 + toolstr.indent_to_str(indent)
    tooltable.print_table(rows=trades, headers=headers, indent=indent)

