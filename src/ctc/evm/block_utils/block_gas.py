from __future__ import annotations

import typing
from typing_extensions import TypedDict

from . import block_crud
from . import block_normalize
from ctc import spec


if typing.TYPE_CHECKING:
    class BlockGasStats(TypedDict):
        base_fee: int | float | None
        min_gas_price: int | float | None
        median_gas_price: int | float | None
        mean_gas_price: float | None
        max_gas_price: int | float | None
        gas_used: int
        gas_limit: int
        n_transactions: int


    class BlocksGasStats(TypedDict):
        min_base_fee: int | float | None
        median_base_fee: int | float | None
        mean_base_fee: int | float | None
        max_base_fee: int | float | None

        min_gas_price: int | float | None
        min_median_gas_price: int | float | None
        min_mean_gas_price: int | float | None
        min_max_gas_price: int | float | None

        median_min_gas_price: int | float | None
        median_median_gas_price: int | float | None
        median_mean_gas_price: int | float | None
        median_max_gas_price: int | float | None

        mean_min_gas_price: int | float | None
        mean_median_gas_price: int | float | None
        mean_gas_price: int | float | None
        mean_max_gas_price: int | float | None

        max_min_gas_price: int | float | None
        max_median_gas_price: int | float | None
        max_mean_gas_price: int | float | None
        max_gas_price: int | float | None

        min_gas_used: int | float | None
        median_gas_used: int | float | None
        mean_gas_used: int | float | None
        max_gas_used: int | float | None

        min_gas_limit: int | float | None
        median_gas_limit: int | float | None
        mean_gas_limit: int | float | None
        max_gas_limit: int | float | None

        min_n_transactions: int | float | None
        median_n_transactions: int | float | None
        mean_n_transactions: int | float | None
        max_n_transactions: int | float | None

        n_blocks: int


async def async_get_block_gas_stats(
    block: spec.BlockNumberReference | spec.Block,
    normalize: bool = True,
    provider: spec.ProviderSpec = None,
) -> BlockGasStats:
    """get gas statistics for a given block"""
    if isinstance(block, dict):
        block_data = block
    else:
        block_data = await block_crud.async_get_block(
            block, include_full_transactions=True, provider=provider
        )

    return get_block_gas_stats(block_data, normalize=normalize)


def get_block_gas_stats(
    block: spec.Block,
    normalize: bool = True,
) -> BlockGasStats:
    import numpy as np

    base_fee: int | float | None = block.get('base_fee_per_gas')

    if len(block['transactions']) > 0:
        if isinstance(block['transactions'][0], str):
            raise Exception(
                'transaction data not in block, use include_full_transactions=True when retrieving block'
            )

        gas_prices: list[int | float] = [
            typing.cast(spec.Transaction, transaction)['gas_price']
            for transaction in block['transactions']
        ]

        if normalize:
            gas_prices = [gas_price / 1e9 for gas_price in gas_prices]
            if base_fee is not None:
                base_fee = base_fee / 1e9

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
        'base_fee': base_fee,
        'min_gas_price': min_gas_price,
        'median_gas_price': median_gas_price,
        'mean_gas_price': mean_gas_price,
        'max_gas_price': max_gas_price,
        'gas_used': block['gas_used'],
        'gas_limit': block['gas_limit'],
        'n_transactions': len(block['transactions']),
    }


async def async_get_gas_stats_by_block(
    blocks: typing.Sequence[spec.BlockNumberReference | spec.Block],
    normalize: bool = True,
    provider: spec.ProviderSpec = None,
) -> list[BlockGasStats]:
    import asyncio

    coroutines = [
        async_get_block_gas_stats(
            block=block,
            normalize=normalize,
            provider=provider,
        )
        for block in blocks
    ]

    return await asyncio.gather(*coroutines)


async def async_get_blocks_gas_stats(
    blocks: typing.Sequence[spec.BlockNumberReference] | None = None,
    start_block: spec.BlockNumberReference | None = None,
    end_block: spec.BlockNumberReference | None = None,
    normalize: bool = True,
    provider: spec.ProviderSpec = None,
) -> BlocksGasStats:
    """get gas statistics aggregated over multiple blocks"""

    if blocks is None:
        if start_block is None or end_block is None:
            raise Exception(
                'must specify blocks or {start_block and end_block}'
            )
        start_block = await block_normalize.async_block_number_to_int(
            block=start_block, provider=provider
        )
        end_block = await block_normalize.async_block_number_to_int(
            block=end_block, provider=provider
        )
        blocks = list(range(start_block, end_block + 1))

    blocks_gas_stats = await async_get_gas_stats_by_block(
        blocks=blocks,
        normalize=normalize,
        provider=provider,
    )

    return aggregate_blocks_gas_stats(blocks_gas_stats=blocks_gas_stats)


def _mmmm(
    items: typing.Sequence[int | float | None],
) -> list[int | float | None]:

    import numpy as np

    non_none = [item for item in items if item is not None]

    median = np.median(non_none)
    if type(non_none[0]) is int:
        typed_median: int | float = int(median)
    else:
        typed_median = float(median)

    if len(items) == 0:
        return [None, None, None, None]
    else:
        return [
            min(non_none),
            typed_median,
            np.mean(non_none),
            max(non_none),
        ]


def aggregate_blocks_gas_stats(
    blocks_gas_stats: typing.Sequence[BlockGasStats],
) -> BlocksGasStats:

    base_fees = [stats['base_fee'] for stats in blocks_gas_stats]
    min_gas_prices = [stats['min_gas_price'] for stats in blocks_gas_stats]
    median_gas_prices = [
        stats['median_gas_price'] for stats in blocks_gas_stats
    ]
    mean_gas_prices = [stats['mean_gas_price'] for stats in blocks_gas_stats]
    max_gas_prices = [stats['max_gas_price'] for stats in blocks_gas_stats]
    gas_useds = [stats['gas_used'] for stats in blocks_gas_stats]
    gas_limits = [stats['gas_limit'] for stats in blocks_gas_stats]
    n_transactionss = [stats['n_transactions'] for stats in blocks_gas_stats]

    min_base_fee, median_base_fee, mean_base_fee, max_base_fee = _mmmm(
        base_fees
    )
    (
        min_gas_price,
        median_min_gas_price,
        mean_min_gas_price,
        max_min_gas_price,
    ) = _mmmm(min_gas_prices)
    (
        min_median_gas_price,
        median_median_gas_price,
        mean_median_gas_price,
        max_median_gas_price,
    ) = _mmmm(median_gas_prices)
    (
        min_mean_gas_price,
        median_mean_gas_price,
        mean_gas_price,
        max_mean_gas_price,
    ) = _mmmm(mean_gas_prices)
    (
        min_max_gas_price,
        median_max_gas_price,
        mean_max_gas_price,
        max_gas_price,
    ) = _mmmm(max_gas_prices)
    (
        min_gas_used,
        median_gas_used,
        mean_gas_used,
        max_gas_used,
    ) = _mmmm(gas_useds)
    (
        min_gas_limit,
        median_gas_limit,
        mean_gas_limit,
        max_gas_limit,
    ) = _mmmm(gas_limits)
    (
        min_n_transactions,
        median_n_transactions,
        mean_n_transactions,
        max_n_transactions,
    ) = _mmmm(n_transactionss)

    return {
        'min_base_fee': min_base_fee,
        'median_base_fee': median_base_fee,
        'mean_base_fee': mean_base_fee,
        'max_base_fee': max_base_fee,
        #
        'min_gas_price': min_gas_price,
        'min_median_gas_price': min_median_gas_price,
        'min_mean_gas_price': min_mean_gas_price,
        'min_max_gas_price': min_max_gas_price,
        #
        'median_min_gas_price': median_min_gas_price,
        'median_median_gas_price': median_median_gas_price,
        'median_mean_gas_price': median_mean_gas_price,
        'median_max_gas_price': median_max_gas_price,
        #
        'mean_min_gas_price': mean_min_gas_price,
        'mean_median_gas_price': mean_median_gas_price,
        'mean_gas_price': mean_gas_price,
        'mean_max_gas_price': mean_max_gas_price,
        #
        'max_min_gas_price': max_min_gas_price,
        'max_median_gas_price': max_median_gas_price,
        'max_mean_gas_price': max_mean_gas_price,
        'max_gas_price': max_gas_price,
        #
        'min_gas_used': min_gas_used,
        'median_gas_used': median_gas_used,
        'mean_gas_used': mean_gas_used,
        'max_gas_used': max_gas_used,
        #
        'min_gas_limit': min_gas_limit,
        'median_gas_limit': median_gas_limit,
        'mean_gas_limit': mean_gas_limit,
        'max_gas_limit': max_gas_limit,
        #
        'min_n_transactions': min_n_transactions,
        'median_n_transactions': median_n_transactions,
        'mean_n_transactions': mean_n_transactions,
        'max_n_transactions': max_n_transactions,
        #
        'n_blocks': len(blocks_gas_stats),
    }
