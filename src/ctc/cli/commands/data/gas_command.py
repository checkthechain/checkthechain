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

from ctc import evm
from ctc import rpc
from ctc.cli import cli_run
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
    last: typing.Optional[typing.Sequence[str]],
    output: str,
    overwrite: bool,
    verbose: bool,
) -> None:

    import numpy as np

    styles = cli_run.get_cli_styles()

    if last is None:
        last_as_int = [10, 100]
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
    raw_median_gas_fees = await evm.async_get_median_blocks_gas_fees(
        block_numbers,
        latest_block_number=latest,
    )

    median_gas_fees = np.array(
        [item['median_gas_fee'] for item in raw_median_gas_fees],
        dtype=float,
    )
    # block_timestamps = await evm.async_get_block_timestamps(block_numbers)
    block_timestamps = [item['timestamp'] for item in raw_median_gas_fees]

    now = time.time()
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

    if verbose:
        print()
        toolstr.print_header(
            'Latest block = '
            + toolstr.add_style(str(latest), styles['metavar']),
            style=styles['title'],
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
            timelength_seconds = round(now - block_timestamps[-last_n])
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

    if output != 'stdout':
        import pandas as pd

        final_df = pd.DataFrame(rows)
        final_df.columns = labels
        final_df = final_df.sort_values(by='time')
        final_df = final_df.set_index('blocks')

        cli_utils.output_data(final_df, output, overwrite=overwrite)
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
                'min': styles['description'],
                'median': styles['description'],
                'mean': styles['description'],
                'max': styles['description'],
            },
        )

        xvals = block_timestamps
        yvals = median_gas_fees
        plot = toolstr.render_line_plot(
            xvals=xvals,
            yvals=yvals,  # type: ignore
            n_rows=40,
            n_columns=120,
            line_style=styles['description'],
            chrome_style=styles['comment'],
            tick_label_style=styles['metavar'],
            xaxis_kwargs={'tick_label_format': 'age'},
            # char_dict='sextants',
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
