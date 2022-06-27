from __future__ import annotations

import typing
import time

from ctc import binary
from ctc import spec

from . import block_crud


async def async_print_block_summary(
    block: spec.Block | spec.BlockNumberReference,
    provider: spec.ProviderReference = None,
) -> None:

    import toolstr
    import tooltime

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
            typing.cast(spec.Transaction, transaction)['gas_price'] / 1e9
            for transaction in block['transactions']
        ]
        import numpy as np

        gas_percentiles = np.percentile(
            gas_prices,
            percentiles,
        )

    title = 'Block ' + str(block['number'])
    toolstr.print_text_box(title)
    print('- timestamp:', block['timestamp'])
    print('- time:', tooltime.timestamp_to_iso(block['timestamp']))
    print('- age:', tooltime.timelength_to_phrase(round(time.time()) - block['timestamp']))
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
        gas_percentiles_str = (
            '('
            + ', '.join(
                [toolstr.format(percentile) for percentile in gas_percentiles]
            )
            + ')'
        )
        print('- gas prices:', percentile_label, '=', gas_percentiles_str)

    message = block['extra_data']
    try:
        message = binary.convert(message, 'binary').decode()
    except Exception as e:
        if len(message) > 80:
            message = message[:77] + '...'
        else:
            message = message
    print('- message:', message)

