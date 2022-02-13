"""
# TODO
- amount burned/issued
    - need to sum up
        - minter rewards (both pre and post 1559)
        - uncle inclusion rewards
        - uncle mining rewards
    - see https://github.com/ethereum/go-ethereum/issues/1644
- amount of time passed in each block aggregation range
- historical blocks and block ranges
- color
"""

import numpy as np
import pandas as pd
import toolstr

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
    df = pd.DataFrame(blocks_gas_stats, index=block_numbers)
    df.index.name = 'block'

    toolstr.print_text_box('Gas Price Summary')
    print()
    toolstr.print_header('Latest block = ' + str(latest))
    for key, value in blocks_gas_stats[-1].items():
        print('-', key + ':', toolstr.format(value))
    print()
    print()
    toolstr.print_header('Previous Blocks')
    print('aggregated using median price of transactions in each block')
    print()
    headers = ['blocks', 'min', 'median', 'mean', 'max']
    rows = []
    for last_n in last:

        row = []
        row.append('last ' + str(last_n) + ' blocks')

        sub_df = df.iloc[-last_n:]
        median_prices = sub_df['median_gas_price'].values
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
    final_df = final_df.set_index('blocks')

    cli_utils.output_data(final_df, output, overwrite)

    await rpc.async_close_http_session()

