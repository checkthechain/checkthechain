from __future__ import annotations

import typing

from ctc import evm
from ctc import rpc
from ctc import spec

from . import contracts
from . import uniswap_v3_spec

if typing.TYPE_CHECKING:
    from typing_extensions import TypedDict

    import tooltime

    class UniswapV3PoolMetadata(TypedDict):
        x_symbol: str
        y_symbol: str
        x_address: str
        y_address: str
        fee: int


#
# # metadata
#


async def async_get_pool_tokens(
    pool_address: spec.Address,
    *,
    context: spec.Context = None,
    **rpc_kwargs: typing.Any,
) -> tuple[spec.Address, spec.Address]:
    import asyncio

    token0_abi = await uniswap_v3_spec.async_get_function_abi('token0', 'pool')
    token1_abi = await uniswap_v3_spec.async_get_function_abi('token1', 'pool')
    kwargs = dict(rpc_kwargs, to_address=pool_address, context=context)
    return await asyncio.gather(
        rpc.async_eth_call(function_abi=token0_abi, **kwargs),
        rpc.async_eth_call(function_abi=token1_abi, **kwargs),
    )


async def async_get_pool_metadata(
    pool_address: spec.Address,
    *,
    context: spec.Context = None,
    **rpc_kwargs: typing.Any,
) -> UniswapV3PoolMetadata:
    x_address, y_address = await async_get_pool_tokens(
        pool_address=pool_address, context=context
    )
    x_symbol, y_symbol = await evm.async_get_erc20s_symbols(
        tokens=[x_address, y_address], context=context, **rpc_kwargs
    )
    fee = await contracts.async_pool_fee(pool_address, context=context)
    return {
        'x_symbol': x_symbol,
        'y_symbol': y_symbol,
        'x_address': x_address,
        'y_address': y_address,
        'fee': fee,
    }


#
# # events
#


async def async_get_pool_swaps(
    pool_address: spec.Address,
    *,
    start_block: spec.BlockNumberReference | None = None,
    end_block: spec.BlockNumberReference | None = None,
    start_time: tooltime.Timestamp | None = None,
    end_time: tooltime.Timestamp | None = None,
    include_timestamps: bool = False,
    replace_symbols: bool = False,
    normalize: bool = True,
    context: spec.Context = None,
) -> spec.DataFrame:
    import asyncio
    import polars as pl

    if normalize or replace_symbols:
        metadata_task = asyncio.create_task(
            async_get_pool_metadata(pool_address, context=context)
        )

    event_abi = await uniswap_v3_spec.async_get_event_abi('Swap', 'pool')

    swaps = await evm.async_get_events(
        event_abi=event_abi,
        contract_address=pool_address,
        start_block=start_block,
        end_block=end_block,
        start_time=start_time,
        end_time=end_time,
        include_timestamps=include_timestamps,
        context=context,
    )

    if normalize or replace_symbols:
        metadata = await metadata_task

    # rename columns
    if replace_symbols:
        x_symbol = metadata['x_symbol']
        y_symbol = metadata['y_symbol']
    else:
        x_symbol = 'x'
        y_symbol = 'y'
    columns = {
        'arg__amount0': x_symbol + '_amount',
        'arg__amount1': y_symbol + '_amount',
    }
    swaps = swaps.rename(columns)

    # normalize columns
    if normalize:
        x_decimals, y_decimals = await evm.async_get_erc20s_decimals(
            tokens=[metadata['x_address'], metadata['y_address']],
            context=context,
        )
        swaps = swaps.with_columns(
            pl.col(columns['arg__amount0']).cast(float) / (10**x_decimals),
            pl.col(columns['arg__amount1']).cast(float) / (10**y_decimals),
        )

    return swaps

