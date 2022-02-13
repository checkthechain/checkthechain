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

import time

import numpy as np
import pandas as pd
import toolstr
import tooltime

from ctc import evm
from ctc import rpc
from ctc.cli import cli_utils


def get_command_spec():
    return {
        'f': async_gas_command,
        'args': [
            {'name': '--last', 'kwargs': {'nargs': '+'}},
            {'name': '--output', 'kwargs': {'default': 'stdout'}},
            {'name': '--overwrite', 'kwargs': {'action': 'store_true'}},
        ],
    }


async def async_gas_command(last, output, overwrite):
    if last is None:
        last = [1, 10, 100]
    else:
        last = [
            int(subtoken.strip(' '))
            for token in last
            for subtoken in token.strip(',').split(',')
        ]

    n_blocks = max(last)
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
    last_times_blocks = []
    for last_time in last_times:
        cutoff_timestamp = now - tooltime.timelength_to_seconds(last_time)
        for i in range(n_blocks):
            if blocks[-i - 1]['timestamp'] < cutoff_timestamp:
                break
        print(i)
        last_times_blocks.append(i)

    toolstr.print_text_box('Gas Price Summary')
    print()
    print('all prices reported in gwei')
    print()
    print()
    toolstr.print_header('Latest block = ' + str(latest))
    for key, value in blocks_gas_stats[-1].items():
        if key in ['gas_limit', 'gas_used']:
            print(
                '-', key + ':', toolstr.format(value, order_of_magnitude=True)
            )
        else:
            print('-', key + ':', toolstr.format(value))
    print()
    print()
    toolstr.print_header('Previous Blocks')
    print('aggregated using median price of transactions in each block')
    print()
    headers = ['blocks', 'time', 'min', 'median', 'mean', 'max']
    rows = []
    for l, last_n in enumerate(last + last_times_blocks):

        row = []

        if l < len(last):
            if last_n == 1:
                row.append('latest block')
            else:
                row.append('last ' + str(last_n) + ' blocks')
            timelength_seconds = round(now - blocks[-last_n]['timestamp'])
            timelength_clock = tooltime.timelength_to_clock(timelength_seconds)
            row.append(timelength_clock)
        else:
            row.append('last ' + last_times[l - len(last)])
            row.append(tooltime.timelength_to_clock(last_times[l - len(last)]))

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
    final_df.columns = headers
    final_df = final_df.sort_values(by='time')
    final_df = final_df.set_index('blocks')

    cli_utils.output_data(final_df, output, overwrite)

    await rpc.async_close_http_session()

