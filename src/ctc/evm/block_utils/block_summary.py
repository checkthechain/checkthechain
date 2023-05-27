from __future__ import annotations

import typing
import time

from ctc import spec
from .. import binary_utils
from .. import transaction_utils
from . import block_crud


async def async_print_block_summary(
    block: spec.DBBlock | spec.BlockNumberReference,
    *,
    context: spec.Context = None,
) -> None:
    """print summary of block"""

    import toolstr
    import tooltime

    from ctc import cli

    if not isinstance(block, dict):
        block = await block_crud.async_get_block(
            block=block, context=context
        )

    block_transactions = await transaction_utils.async_get_block_transactions(
        block['number'], context=context
    )
    percentiles = [
        0,
        5,
        50,
        95,
        100,
    ]

    gas_prices = []
    for transaction in block_transactions:
        gas_prices.append(transaction['gas_price'] / 1e9)
    import numpy as np

    gas_percentiles: typing.Sequence[typing.Any] | spec.NumpyArray
    if len(gas_prices) > 0:
        gas_percentiles = np.percentile(
            gas_prices,
            percentiles,
        )
    else:
        gas_percentiles = [None] * len(percentiles)

    title = 'Block ' + str(block['number'])
    styles = cli.get_cli_styles()
    toolstr.print_text_box(title, style=styles['title'])
    cli.print_bullet(key='timestamp', value=block['timestamp'])
    cli.print_bullet(
        key='time', value=tooltime.timestamp_to_iso(block['timestamp'])
    )
    cli.print_bullet(
        key='age',
        value=tooltime.timelength_to_phrase(
            round(time.time()) - block['timestamp']
        ),
    )
    cli.print_bullet(key='block_hash', value=block['hash'])
    cli.print_bullet(key='n_transactions', value=len(block_transactions))
    cli.print_bullet(
        key='gas used',
        value=(
            toolstr.format(block['gas_used'])
            + ' / '
            + toolstr.format(block['gas_limit'])
        ),
    )

    if block_transactions is not None:
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
        cli.print_bullet(
            key='gas prices:',
            value=percentile_label + '=' + gas_percentiles_str,
        )

    message = block['extra_data']
    try:
        message = binary_utils.to_binary(message).decode()
    except Exception:
        if len(message) > 80:
            message = message[:77] + '...'
        else:
            message = message
    cli.print_bullet(key='message', value=message)

