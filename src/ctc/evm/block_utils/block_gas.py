from __future__ import annotations

from ctc import rpc


async def async_get_block_gas_stats(block, normalize=True):
    if not isinstance(block, dict):
        if isinstance(block, str) and block.startswith('0x') and len(block) == 66:
            block = await rpc.async_eth_get_block_by_hash(block)
        else:
            block = await rpc.async_eth_get_block_by_number(block)
    return get_block_gas_stats(block)


def get_block_gas_stats(block, normalize=True):
    import numpy as np

    base_fee = block.get('base_fee_per_gas')

    if len(block['transactions']) > 0:
        if isinstance(block['transactions'][0], str):
            raise Exception('transaction data not in block')

        gas_prices = [
            transaction['gas_price'] for transaction in block['transactions']
        ]

        if normalize:
            gas_prices = [gas_price / 1e9 for gas_price in gas_prices]
            if base_fee is not None:
                base_fee /= 1e9

        min_gas_price = min(gas_prices)
        median_gas_price = np.median(gas_prices)
        mean_gas_price = sum(gas_prices) / len(gas_prices)
        max_gas_price = max(gas_prices)

    else:
        min_gas_price = None
        median_gas_price = None
        mean_gas_price = None
        max_gas_price = None

    return {
        'base_fee': base_fee,
        'min_gas_price': min_gas_price,
        'median_gas_price': median_gas_price,
        'mean_gas_price': mean_gas_price,
        'max_gas_price': max_gas_price,
        'gas_limit': block['gas_limit'],
        'gas_used': block['gas_used'],
        'n_transactions': len(block['transactions']),
    }

