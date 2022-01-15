import tooltime
import toolstr

from ctc import binary
from . import block_crud


async def async_print_block_summary(block, provider=None):

    if not isinstance(block, dict):
        block = await block_crud.async_get_block(block=block, provider=provider)

    full_transactions = len(block['transactions']) > 0 and isinstance(
        block['transactions'][0], dict
    )
    percentiles = [
        0,
        5,
        50,
        95,
        100,
    ]

    if full_transactions:
        gas_prices = [
            transaction['gas_price'] / 1e9
            for transaction in block['transactions']
        ]
        import numpy as np

        gas_percentiles = np.percentile(
            gas_prices,
            percentiles,
        )

    title = 'Block ' + str(block['number'])
    print(title)
    print('─' * len(title))
    print('- timestamp:', block['timestamp'])
    print('- time:', tooltime.timestamp_to_iso(block['timestamp']))
    print('- block_hash:', block['hash'])
    print('- n_transactions:', len(block['transactions']))
    print(
        '- gas used:',
        toolstr.format(block['gas_used']),
        '/',
        toolstr.format(block['gas_limit']),
    )
    if full_transactions:
        percentile_label = (
            '('
            + ', '.join([str(percentile) + '%' for percentile in percentiles])
            + ')'
        )
        gas_percentiles = (
            '('
            + ', '.join(
                [toolstr.format(percentile) for percentile in gas_percentiles]
            )
            + ')'
        )
        print('- gas prices:', percentile_label, '=', gas_percentiles)

    message = block['extra_data']
    try:
        message = binary.convert(message, 'binary').decode()
    except Exception as e:
        if len(message) > 80:
            message = message[:77] + '...'
        else:
            message = message
    print('- message:', message)

