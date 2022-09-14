"""
# TODO
- amount burned/issued
    - need to sum up
        - minter rewards (both pre and post 1559)
        - uncle inclusion rewards
        - uncle mining rewards
    - see https://github.com/ethereum/go-ethereum/issues/1644
- amount of time in each block aggregation range
- historical blocks and block ranges
- color


use statistical sampling to get quick daily/weekly/monthly avg's
"""

from __future__ import annotations

import time
import typing

import toolcli
import toolstr
import tooltime

from ctc import cli
from ctc import evm
from ctc import rpc
from ctc.cli import cli_utils


def get_command_spec() -> toolcli.CommandSpec:
    return {
        'f': async_gas_command,
        'help': 'output gas summary of block range',
        'args': [
            # {
            #     'name': 'last',
            #     'help': 'either amount of blocks (e.g. 100) or time (e.g. 24h)',
            #     'nargs': '?',
            # },
            {
                'name': '--block',
                'help': 'historical block to use',
                'type': int,
            },
            {
                'name': '--last',
                'metavar': 'N',
                'nargs': '+',
                'help': 'number of blocks to include',
            },
            {
                'name': '--export',
                'default': 'stdout',
                'help': 'file path for output (.json or .csv)',
            },
            {
                'name': '--overwrite',
                'action': 'store_true',
                'help': 'specify that output path can be overwritten',
            },
            {
                'name': ['-v', '--verbose'],
                'action': 'store_true',
                'help': 'output additional information',
            },
        ],
        'examples': [
            '',
            '--last 300',
        ],
    }


async def async_gas_command(
    *,
    block: int | None,
    last: typing.Optional[typing.Sequence[str]],
    export: str,
    overwrite: bool,
    verbose: bool,
) -> None:

    import numpy as np

    styles = cli.get_cli_styles()

    if last is None:
        last_as_int = [10, 100]
    else:
        last_as_int = [
            int(subtoken.strip(' '))
            for token in last
            for subtoken in token.strip(',').split(',')
        ]

    n_blocks = max(last_as_int)
    if block is None:
        block = await rpc.async_eth_block_number()
        using_latest = True
    else:
        using_latest = False
    block_numbers = list(range(block - n_blocks + 1, block + 1))

    # get block transaction data
    raw_median_gas_fees = await evm.async_get_median_blocks_gas_fees(
        block_numbers,
        latest_block_number=block,
    )

    median_gas_fees = np.array(
        [item['median_gas_fee'] for item in raw_median_gas_fees],
        dtype=float,
    )
    # block_timestamps = await evm.async_get_block_timestamps(block_numbers)
    block_timestamps = [item['timestamp'] for item in raw_median_gas_fees]

    if using_latest:
        now = time.time()
    else:
        now = block_timestamps[-1]
    last_times = ['5 minutes', '10 minutes']
    last_blocks = []
    for last_as_int_time in last_times:
        cutoff_timestamp = now - tooltime.timelength_to_seconds(
            last_as_int_time
        )
        for i in range(n_blocks):
            if block_timestamps[-i - 1] < cutoff_timestamp:
                break
        last_blocks.append(i)

    toolstr.print_text_box('Gas Price Summary', style=styles['title'])
    print()
    toolstr.print('all prices reported in gwei', style=styles['comment'])

    print()
    toolstr.print_header('Latest Block Summary', style=styles['title'])
    print()
    toolstr.print(
        'using block ' + toolstr.add_style(str(block), styles['metavar']),
        style=styles['comment'],
    )
    block_rows = []
    block_gas_stats = await evm.async_get_block_gas_stats(
        block_numbers[-1],
    )
    for key, value in block_gas_stats.items():
        if key in ['gas_limit', 'gas_used']:
            block_row = (
                key,
                toolstr.format(value, order_of_magnitude=True),
            )
        else:
            if value is None:
                if key == 'base_fee':
                    block_row = (key, '-')
                else:
                    block_row = (key, '\[no txs]')
            else:
                block_row = (key, toolstr.format(value))
        block_rows.append(block_row)
    print()
    toolstr.print_table(
        block_rows,
        border=styles['comment'],
        column_styles=[styles['option'], styles['description'] + ' bold'],
        indent=4,
    )

    if verbose:
        print()
        print()
        toolstr.print_header(
            'Costs of Common Operations', style=styles['title']
        )
        from ctc.protocols import chainlink_utils

        recent_median_gas_fee = median_gas_fees[~np.isnan(median_gas_fees)][-1]

        try:
            eth_usd: float | None = await chainlink_utils.async_get_eth_price(
                block=block
            )
        except Exception:
            eth_usd = None
        print()
        message = 'using gas price = ' + toolstr.add_style(
            toolstr.format(recent_median_gas_fee) + ' gwei',
            styles['description'] + ' bold',
        )
        if eth_usd is not None:
            message += ' and ETH price = ' + toolstr.add_style(
                toolstr.format(eth_usd, prefix='$'),
                styles['description'] + ' bold',
            )
        toolstr.print(message, style=styles['comment'])
        print()
        await async_print_gas_costs(
            eth_usd=eth_usd,
            gas_fee=recent_median_gas_fee,
        )

    print()
    print()
    toolstr.print_header('Previous Blocks', style=styles['title'])
    print()
    toolstr.print(
        'aggregated by median transaction price of each block',
        style=styles['comment'],
    )
    print()
    labels = ['', 'blocks', 'time', 'min', 'median', 'mean', 'max']
    rows: typing.MutableSequence[typing.Any] = []
    for index, last_n in enumerate(last_as_int + last_blocks):

        row: list[typing.Union[str, None, int, float]] = []

        if index < len(last_as_int):
            if last_n == 1:
                row.append('latest block')
            else:
                row.append('last ' + str(last_n) + ' blocks')
            row.append(last_n)
            if using_latest:
                timelength_seconds = round(now - block_timestamps[-last_n])
            else:
                timelength_seconds = (
                    block_timestamps[-1] - block_timestamps[-last_n]
                )
            timelength_clock = tooltime.timelength_to_clock(timelength_seconds)
            timelength_clock = timelength_clock.lstrip('0').lstrip(':')
            row.append(timelength_clock)
        else:
            row.append('last ' + last_times[index - len(last_as_int)])
            row.append(last_n)
            timelength_clock = tooltime.timelength_to_clock(
                last_times[index - len(last_as_int)]
            )
            timelength_clock = timelength_clock.lstrip('0').lstrip(':')
            row.append(timelength_clock)

        # add gas fee columns
        interval_median_gas_fees = median_gas_fees[-last_n:]
        if len(interval_median_gas_fees) > 0:
            row.append(np.nanmin(interval_median_gas_fees))
            row.append(np.nanmedian(interval_median_gas_fees))
            row.append(np.nanmean(interval_median_gas_fees))
            row.append(np.nanmax(interval_median_gas_fees))
        else:
            row.extend([None] * 4)

        rows.append(row)

    if export != 'stdout':
        import pandas as pd

        final_df = pd.DataFrame(rows)
        final_df.columns = labels
        final_df = final_df.sort_values(by='time')
        final_df = final_df.set_index('blocks')

        cli_utils.output_data(final_df, export, overwrite=overwrite)
    else:
        toolstr.print_table(
            rows=rows,
            labels=labels,
            border=styles['comment'],
            label_style=styles['title'],
            column_formats={
                'min': {'decimals': 1, 'trailing_zeros': True},
                'median': {'decimals': 1, 'trailing_zeros': True},
                'mean': {'decimals': 1, 'trailing_zeros': True},
                'max': {'decimals': 1, 'trailing_zeros': True},
            },
            column_styles={
                '': styles['metavar'],
                'blocks': styles['metavar'],
                'time': styles['metavar'],
                'min': styles['description'] + ' bold',
                'median': styles['description'] + ' bold',
                'mean': styles['description'] + ' bold',
                'max': styles['description'] + ' bold',
            },
        )

        xvals = block_timestamps
        yvals = median_gas_fees
        if using_latest:
            xtick_format = 'age'
            n_ticks = 3
        else:
            xtick_format = 'iso'
            n_ticks = 2
        plot = toolstr.render_line_plot(
            xvals=xvals,
            yvals=yvals,  # type: ignore
            n_rows=40,
            n_columns=120,
            line_style=styles['description'],
            chrome_style=styles['comment'],
            tick_label_style=styles['metavar'],
            xaxis_kwargs={
                'tick_label_format': xtick_format,
                'n_ticks': n_ticks,
            },
            # char_dict='sextants',
        )
        print()
        print()
        toolstr.print(
            toolstr.hjustify('median fee', 'center', 70),
            indent=4,
            style=styles['title'],
        )
        toolstr.print(plot, indent=4)


async def async_print_gas_costs(
    *, gas_fee: float, eth_usd: float | None
) -> None:

    styles = cli.get_cli_styles()

    # see appendices G+H https://ethereum.github.io/yellowpaper/paper.pdf
    rows: typing.Sequence[typing.MutableSequence[typing.Any]] = [
        ['tx execution', 21000, 'gas per tx'],
        ['call data  (0)', 4, 'gas per byte'],
        ['call data (!0)', 16, 'gas per byte'],
        ['contract creation', 32000, 'gas per contract'],
        ['contract bytecode', 200, 'gas per byte'],
        ['contract destruct', -24000, 'gas per contract'],
        ['storage  0 --> !0', 20000 / 32, 'gas per byte'],
        ['storage  0 -->  0', 2900 / 32, 'gas per byte'],
        ['storage !0 -->  0', -15000 / 32, 'gas per byte'],
        ['log creation', 375, 'gas per log'],
        ['log topic', 375, 'gas per topic'],
        ['log data', 8, 'gas per byte'],
    ]
    labels = ['', 'gas cost', 'gas units']
    column_styles = [
        styles['metavar'],
        styles['description'] + ' bold',
        styles['option'],
    ]

    if eth_usd is not None:
        for row in rows:
            raw_gas_amount: int = row[1]
            gas_amount = float(raw_gas_amount)
            usd_cost = eth_usd * gas_fee * gas_amount / 1e9
            row.append(abs(usd_cost))
            row.append(row[2].replace('gas', '$'))
        labels.append('$ cost')
        labels.append('$ units')
        column_styles.append(styles['description'] + ' bold')
        column_styles.append(styles['option'])

    toolstr.print_table(
        rows,
        labels=labels,
        border=styles['comment'],
        label_style=styles['title'],
        column_styles=column_styles,
        column_formats={
            '$ cost': {
                'decimals': 5,
                'trailing_zeros': True,
                # 'scientific': False,
                'prefix': '$',
            },
        },
        column_gap=1,
        # compact=2,
        # indent=4,
    )
    print()
    toolstr.print(
        'for complete gas accounting see yellowpaper:\n    https://ethereum.github.io/yellowpaper/paper.pdf',
        style=styles['comment'],
        indent=4,
    )
