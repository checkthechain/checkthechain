import asyncio

import toolstr
import numpy as np

from ctc import evm
from ctc import rpc


def get_command_spec():
    return {
        'f': gas_command,
    }


def gas_command(**kwargs):
    asyncio.run(run())


async def run():

    block = await evm.async_get_block('latest', include_full_transactions=True)
    base_fee = toolstr.format(block['base_fee_per_gas'] / 1e9)

    toolstr.print_text_box('Gas for block ' + str(block['number']))
    print('- base fee:', base_fee, 'gwei')
    if len(block['transactions']) == 0:
        print('[no transactions]')
        return

    # compute gas prices
    gas_prices = [
        transaction['gas_price'] for transaction in block['transactions']
    ]
    if len(gas_prices) == 0:
        mean_gas = '[no transactions]'
    else:
        mean_gas = sum(gas_prices) / len(gas_prices)
        mean_gas = toolstr.format(mean_gas / 1e9)
    median_gas = np.median(gas_prices)
    median_gas = toolstr.format(median_gas / 1e9)
    max_gas = max(gas_prices)
    max_gas = toolstr.format(max_gas / 1e9)
    min_gas = min(gas_prices)
    min_gas = toolstr.format(min_gas / 1e9)

    print('- mean gas:', mean_gas, 'gwei')
    print(
        '- [min, median, max] gas =',
        '[' + min_gas + ',',
        median_gas + ',',
        max_gas + '] gwei',
    )

    await rpc.async_close_http_session()

