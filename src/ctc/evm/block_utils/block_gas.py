from __future__ import annotations

import os
import typing

from . import block_crud
from ctc import evm
from ctc import spec

if typing.TYPE_CHECKING or os.environ.get('BUILDING_SPHINX') == '1':

    from typing_extensions import TypedDict
    from ctc import db

    class BlockGasStats(TypedDict):
        base_fee: int | float | None
        min_gas_price: int | float | None
        median_gas_price: int | float | None
        mean_gas_price: float | None
        max_gas_price: int | float | None
        gas_used: int
        gas_limit: int
        n_transactions: int


def compute_median_block_gas_fee(
    block: spec.Block,
    *,
    normalize: bool,
) -> int | float | None:
    """compute median gas fee of transactions in block"""

    import numpy as np

    # get transactions
    transactions = block['transactions']
    if len(transactions) == 0:
        return None

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

    # normalize
    if normalize:
        median = median / 1e9

    return median


def compute_median_blocks_gas_fees(
    blocks: typing.Sequence[spec.Block],
    *,
    normalize: bool = True,
) -> typing.Sequence[int | float | None]:
    """compute median gas fees of transactionss in multiple blocks"""

    return [
        compute_median_block_gas_fee(block, normalize=normalize)
        for block in blocks
    ]


async def async_get_median_block_gas_fee(
    block: spec.BlockNumberReference,
    *,
    normalize: bool = True,
    use_db: bool = True,
    network: spec.NetworkReference | None = None,
    provider: spec.ProviderReference = None,
) -> db.BlockGasRow:
    """get median gas fee for a given block"""

    from ctc import rpc

    network, provider = evm.get_network_and_provider(network, provider)
    block = await evm.async_block_number_to_int(block, provider=provider)

    if use_db:
        from ctc import db

        try:
            result = await db.async_query_median_block_gas_fee(
                block, network=network
            )

            if result is not None:
                if normalize and result['median_gas_fee'] is not None:
                    result['median_gas_fee'] /= 1e9

                return result

        except Exception:
            pass

    block_data = await rpc.async_eth_get_block_by_number(
        block,
        provider=provider,
        include_full_transactions=True,
    )
    return {
        'block_number': block,
        'timestamp': block_data['timestamp'],
        'median_gas_fee': compute_median_block_gas_fee(
            block_data,
            normalize=normalize,
        ),
    }


async def async_get_median_blocks_gas_fees(
    blocks: typing.Sequence[spec.BlockNumberReference],
    *,
    use_db: bool = True,
    normalize: bool = True,
    network: spec.NetworkReference | None = None,
    provider: spec.ProviderReference = None,
    verbose: bool = True,
    latest_block_number: int | None = None,
) -> typing.Sequence[db.BlockGasRow]:
    """get median gas fees for multiple blocks"""

    network, provider = evm.get_network_and_provider(network, provider)
    blocks = await evm.async_block_numbers_to_int(blocks)

    # get data from db
    if use_db:
        from ctc import db

        result = await db.async_query_median_blocks_gas_fees(
            blocks, network=network
        )

        if result is None:
            fee_map: typing.MutableMapping[int, db.BlockGasRow] = {}
            missing = blocks
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
        blocks_data = await evm.async_get_blocks(
            blocks=missing,
            include_full_transactions=True,
            provider={'chunk_size': 1},
            latest_block_number=latest_block_number,
        )

        missing_fees = compute_median_blocks_gas_fees(
            blocks_data,
            normalize=False,
        )
        for block, block_data, fee in zip(missing, blocks_data, missing_fees):
            fee_map[block] = {
                'block_number': block,
                'median_gas_fee': fee,
                'timestamp': block_data['timestamp'],
            }

    if normalize:
        for block, fee_data in fee_map.items():
            if fee_data is not None and fee_data['median_gas_fee'] is not None:
                fee_data['median_gas_fee'] /= 1e9

    return [fee_map[block] for block in blocks]


async def async_get_block_gas_stats(
    block: spec.BlockNumberReference | spec.Block,
    *,
    normalize: bool = True,
    provider: spec.ProviderReference = None,
) -> BlockGasStats:
    """get gas usage statistics for a given block"""
    if isinstance(block, dict):
        block_data = block
    else:
        block_data = await block_crud.async_get_block(
            block, include_full_transactions=True, provider=provider
        )

    return compute_block_gas_stats(block_data, normalize=normalize)


async def async_get_gas_stats_by_block(
    blocks: typing.Sequence[spec.BlockNumberReference | spec.Block],
    *,
    normalize: bool = True,
    provider: spec.ProviderReference = None,
) -> list[BlockGasStats]:
    """get block gas usage statistics of multiple blocks"""

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


def compute_block_gas_stats(
    block: spec.Block,
    *,
    normalize: bool = True,
) -> BlockGasStats:
    """compute gas usage statistics for given block"""
    import numpy as np

    base_fee: int | float | None = block.get('base_fee_per_gas')

    if len(block['transactions']) > 0:
        if isinstance(block['transactions'][0], str):
            raise Exception(
                'transaction data not in block, use include_full_transactions=True when retrieving block'
            )

        gas_prices: list[int | float] = [
            transaction['gas_price']  # type: ignore
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
