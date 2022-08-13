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
"""

from __future__ import annotations

import time
import typing

import toolcli
import toolstr
import tooltime

from ctc import evm
from ctc import rpc
from ctc.cli import cli_run
from ctc.cli import cli_utils


def get_command_spec() -> toolcli.CommandSpec:
    return {
        'f': async_gas_command,
        'help': 'output gas summary of block range',
        'args': [
            {
                'name': '--last',
                'metavar': 'N',
                'nargs': '+',
                'help': 'number of blocks to include',
            },
            {
                'name': '--output',
                'default': 'stdout',
                'help': 'file path for output (.json or .csv)',
            },
            {
                'name': '--overwrite',
                'action': 'store_true',
                'help': 'specify that output path can be overwritten',
            },
        ],
        'examples': [
            '',
            '--last 300',
        ],
    }


async def async_gas_command(
    *,
    last: typing.Optional[typing.Sequence[str]],
    output: str,
    overwrite: bool,
) -> None:

    import numpy as np
    import pandas as pd

    styles = cli_run.get_cli_styles()

    if last is None:
        last_as_int = [1, 10, 100]
    else:
        last_as_int = [
            int(subtoken.strip(' '))
            for token in last
            for subtoken in token.strip(',').split(',')
        ]

    n_blocks = max(last_as_int)
    latest = await rpc.async_eth_block_number()
    block_numbers = list(range(latest - n_blocks + 1, latest + 1))

    # get block transaction data
    blocks = await rpc.async_batch_eth_get_block_by_number(
        block_numbers=block_numbers,
        provider={'chunk_size': 1},
    )

    # compute block gas stats
    blocks_gas_stats = [evm.get_block_gas_stats(block) for block in blocks]
    gas_stats_df = pd.DataFrame(blocks_gas_stats, index=block_numbers)
    gas_stats_df.index.name = 'block'

    now = time.time()
    last_times = ['5 minutes', '10 minutes']
    last_blocks = []
    for last_as_int_time in last_times:
        cutoff_timestamp = now - tooltime.timelength_to_seconds(
            last_as_int_time
        )
        for i in range(n_blocks):
            if blocks[-i - 1]['timestamp'] < cutoff_timestamp:
                break
        last_blocks.append(i)

    toolstr.print_text_box('Gas Price Summary', style=styles['title'])
    print()
    toolstr.print('all prices reported in gwei', style=styles['comment'])
    print()
    toolstr.print_header(
        'Latest block = ' + toolstr.add_style(str(latest), styles['metavar']),
        style=styles['title'],
    )
    block_rows = []
    for key, value in blocks_gas_stats[-1].items():
        if key in ['gas_limit', 'gas_used']:
            block_row = (key, toolstr.format(value, order_of_magnitude=True))
        else:
            if value is None:
                block_row = (key, '')
            else:
                block_row = (key, toolstr.format(value))
        block_rows.append(block_row)
    print()
    toolstr.print_table(
        block_rows,
        border=styles['comment'],
        column_styles=[styles['option'], styles['description']],
        indent=4,
    )
    print()
    print()
    toolstr.print_header('Previous Blocks', style=styles['title'])
    print()
    toolstr.print(
        'aggregated by median transactoin price of each block',
        style=styles['comment'],
    )
    print()
    labels = ['blocks', 'time', 'min', 'median', 'mean', 'max']
    rows = []
    for l, last_n in enumerate(last_as_int + last_blocks):

        row: list[typing.Union[str, None, int, float]] = []

        if l < len(last_as_int):
            if last_n == 1:
                row.append('latest block')
            else:
                row.append('last ' + str(last_n) + ' blocks')
            timelength_seconds = round(now - blocks[-last_n]['timestamp'])
            timelength_clock = tooltime.timelength_to_clock(timelength_seconds)
            row.append(timelength_clock)
        else:
            row.append('last ' + last_times[l - len(last_as_int)])
            row.append(
                tooltime.timelength_to_clock(last_times[l - len(last_as_int)])
            )

        sub_gas_stats_df = gas_stats_df.iloc[-last_n:]
        median_prices = sub_gas_stats_df['median_gas_price'].values
        median_prices = median_prices[~np.isnan(median_prices)]

        if len(median_prices) > 0:
            row.append(median_prices.min())
            row.append(np.median(median_prices))
            row.append(median_prices.mean())
            row.append(median_prices.max())
        else:
            row.extend([None] * 4)

        rows.append(row)

    final_df = pd.DataFrame(rows)
    final_df.columns = labels
    final_df = final_df.sort_values(by='time')
    final_df = final_df.set_index('blocks')

    if output != 'stdout':
        cli_utils.output_data(final_df, output, overwrite=overwrite)
    else:
        toolstr.print_dataframe_as_table(
            final_df,
            border=styles['comment'],
            label_style=styles['title'],
            column_styles={
                'blocks': styles['metavar'],
                'time': styles['description'],
                'min': styles['description'],
                'median': styles['description'],
                'mean': styles['description'],
                'max': styles['description'],
            },
        )

        xvals = [block['timestamp'] for block in blocks]
        yvals = gas_stats_df['median_gas_price'].values
        plot = toolstr.render_line_plot(
            xvals=xvals,
            yvals=yvals,  # type: ignore
            n_rows=40,
            n_columns=120,
            line_style=styles['description'],
            chrome_style=styles['comment'],
            tick_label_style=styles['metavar'],
            xtick_format='age',
        )
        print()
        print()
        print()
        toolstr.print(
            toolstr.hjustify('median fee', 'center', 70),
            indent=4,
            style=styles['title'],
        )
        toolstr.print(plot, indent=4)
