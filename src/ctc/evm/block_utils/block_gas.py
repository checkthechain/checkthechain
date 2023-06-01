from __future__ import annotations

import os
import typing

from .. import transaction_utils
from . import block_times
from . import block_normalize
from ctc import evm
from ctc import spec

if typing.TYPE_CHECKING or os.environ.get('BUILDING_SPHINX') == '1':

    from typing_extensions import TypedDict
    from ctc import db

    class BlockGasStats(TypedDict):
        min_gas_price: int | float | None
        median_gas_price: int | float | None
        mean_gas_price: float | None
        max_gas_price: int | float | None
        n_transactions: int
        # base_fee: int | float | None
        # gas_used: int
        # gas_limit: int


#
# # query median gas fees
#


async def async_get_median_block_gas_fee(
    block: spec.BlockNumberReference,
    *,
    normalize: bool = True,
    context: spec.Context = None,
) -> db.BlockGasRow:
    """get median gas fee for a given block"""

    from ctc import config
    from ctc import rpc

    block = await evm.async_block_number_to_int(block, context=context)

    read_cache, write_cache = config.get_context_cache_read_write(
        schema_name='block_gas', context=context
    )
    if read_cache:
        from ctc import db

        try:
            result = await db.async_query_median_block_gas_fee(
                block, context=context
            )

            if result is not None:
                if normalize and result['median_gas_fee'] is not None:
                    result['median_gas_fee'] /= 1e9

                return result

        except Exception:
            pass

    block_timestamp = await block_times.async_get_block_timestamp(
        block=block, context=context
    )
    txs = await transaction_utils.async_get_block_transactions(
        block, context=context
    )
    return {
        'block_number': block,
        'timestamp': block_timestamp,
        'median_gas_fee': compute_transactions_median_gas_fee(
            txs,
            normalize=normalize,
        ),
    }


async def async_get_median_blocks_gas_fees(
    blocks: typing.Sequence[spec.BlockNumberReference],
    *,
    normalize: bool = True,
    verbose: bool = True,
    latest_block_number: int | None = None,
    context: spec.Context = None,
) -> typing.Sequence[db.BlockGasRow]:
    """get median gas fees for multiple blocks"""

    from ctc import config

    blocks = await evm.async_block_numbers_to_int(blocks)

    # get data from db
    read_cache, write_cache = config.get_context_cache_read_write(
        schema_name='block_gas', context=context
    )
    if read_cache:
        from ctc import db

        result = await db.async_query_median_blocks_gas_fees(
            blocks, context=context
        )

        if result is None:
            fee_map: typing.MutableMapping[int, db.BlockGasRow] = {}
            missing: typing.Sequence[int] = blocks
        else:
            fee_map = dict(result)
            missing = []
            for block in blocks:
                if block not in fee_map:
                    missing.append(block)
    else:
        fee_map = {}

    # get data from rpc
    if len(missing) > 0:
        if verbose:
            import toolstr
            from ctc import cli

            styles = cli.get_cli_styles()
            toolstr.print(
                'fetching tx gas data for '
                + toolstr.add_style(
                    str(len(missing)), styles['description'] + ' bold'
                )
                + ' blocks',
            )
            print()

        from ctc import config

        context = config.update_context(
            context, merge_provider={'chunk_size': 1}
        )

        # get txs by block
        txs = await transaction_utils.async_get_blocks_transactions(
            blocks=missing,
            context=context,
        )
        blocks_timestamps = await block_times.async_get_block_timestamps(
            blocks=blocks, context=context
        )
        txs_by_block: dict[int, list[spec.DBTransaction]] = {}
        for tx in txs:
            block = tx['block_number']
            txs_by_block.setdefault(block, [])
            txs_by_block[block].append(tx)

        for block, timestamp in zip(missing, blocks_timestamps):
            fee = compute_transactions_median_gas_fee(
                txs_by_block[block], normalize=normalize
            )
            fee_map[block] = {
                'block_number': block,
                'median_gas_fee': fee,
                'timestamp': timestamp,
            }

    if normalize:
        for block, fee_data in fee_map.items():
            if fee_data is not None and fee_data['median_gas_fee'] is not None:
                fee_data['median_gas_fee'] /= 1e9

    return [fee_map[block] for block in blocks]


#
# # query gas stats
#


async def async_get_block_gas_stats(
    block: spec.BlockNumberReference,
    *,
    normalize: bool = True,
    context: spec.Context = None,
) -> BlockGasStats:
    """get gas usage statistics for a given block"""

    block_number = await block_normalize.async_block_reference_to_int(
        block=block, context=context
    )
    txs = await transaction_utils.async_get_block_transactions(
        block=block_number, context=context
    )
    return compute_transactions_gas_stats(txs, normalize=normalize)


async def async_get_gas_stats_by_block(
    blocks: typing.Sequence[spec.BlockNumberReference],
    *,
    normalize: bool = True,
    context: spec.Context = None,
) -> list[BlockGasStats]:
    """get block gas usage statistics of multiple blocks"""

    # get txs of blocks
    int_blocks = await block_normalize.async_block_numbers_to_int(
        blocks=blocks, context=context
    )
    txs = await transaction_utils.async_get_blocks_transactions(
        blocks=int_blocks, context=context
    )

    # sort txs by block
    txs_by_block: dict[int, list[spec.DBTransaction]] = {}
    for tx in txs:
        block = tx['block_number']
        txs_by_block.setdefault(block, [])
        txs_by_block[block].append(tx)

    # compute stats per block
    return [
        compute_transactions_gas_stats(
            txs_by_block[int_block], normalize=normalize
        )
        for int_block in int_blocks
    ]


#
# # compute gas stats
#


def compute_transactions_median_gas_fee(
    transactions: typing.Sequence[spec.DBTransaction],
    *,
    normalize: bool,
) -> int | float | None:
    """compute median gas fee of transactions in block"""

    import numpy as np

    # gather gas fees
    gas_fees = []
    for transaction in transactions:
        if isinstance(transaction, str):
            raise Exception(
                'must use a block with include_full_transactions=True'
            )
        gas_fees.append(transaction['gas_price'])

    # compute median
    median = float(np.median(gas_fees))

    # # normalize
    # if normalize:
    #     median = median / 1e9

    return median


def compute_transactions_gas_stats(
    transactions: typing.Sequence[spec.DBTransaction],
    *,
    normalize: bool = True,
) -> BlockGasStats:
    """compute gas usage statistics for given block"""

    import numpy as np

    if len(transactions) > 0:

        gas_prices: list[int | float] = [
            transaction['gas_price'] for transaction in transactions
        ]

        if normalize:
            gas_prices = [gas_price / 1e9 for gas_price in gas_prices]

        min_gas_price = min(gas_prices)
        median_gas_price = float(np.median(gas_prices))
        mean_gas_price = sum(gas_prices) / len(gas_prices)
        max_gas_price = max(gas_prices)

    else:
        min_gas_price = None
        median_gas_price = None
        mean_gas_price = None
        max_gas_price = None

    return {
        'min_gas_price': min_gas_price,
        'median_gas_price': median_gas_price,
        'mean_gas_price': mean_gas_price,
        'max_gas_price': max_gas_price,
        'n_transactions': len(transactions),
    }


# def compute_block_gas_stats(block: spec.DBBlock, normalize: bool = False):
#     base_fee: int | float | None = block.get('base_fee_per_gas')
#     if normalize:
#         if base_fee is not None:
#             base_fee = base_fee / 1e9
#     return {
#         'base_fee': base_fee,
#         'gas_used': block['gas_used'],
#         'gas_limit': block['gas_limit'],
#     }

