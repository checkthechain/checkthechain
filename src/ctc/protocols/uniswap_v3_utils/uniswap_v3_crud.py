from __future__ import annotations

import asyncio
import typing
from typing_extensions import TypedDict

from ctc import evm
from ctc import rpc
from ctc import spec

from . import contracts
from . import uniswap_v3_spec


class UniswapV3PoolMetadata(TypedDict):
    x_symbol: str
    y_symbol: str
    x_address: str
    y_address: str
    fee: int


#
# # metadata
#


async def download_pool_abi(pool_address: spec.Address) -> None:
    example_pool = '0x8f8ef111b67c04eb1641f5ff19ee54cda062f163'
    await evm.async_save_proxy_contract_abi_to_filesystem(
        contract_address=pool_address,
        proxy_implementation=example_pool,
    )


async def async_get_pool_tokens(
    pool_address: spec.Address,
    **rpc_kwargs: typing.Any,
) -> tuple[spec.Address, spec.Address]:
    token0_abi = await uniswap_v3_spec.async_get_function_abi('token0', 'pool')
    token1_abi = await uniswap_v3_spec.async_get_function_abi('token1', 'pool')
    kwargs = dict(rpc_kwargs, to_address=pool_address)
    return await asyncio.gather(
        rpc.async_eth_call(function_abi=token0_abi, **kwargs),
        rpc.async_eth_call(function_abi=token1_abi, **kwargs),
    )


async def async_get_pool_metadata(
    pool_address: spec.Address,
    **rpc_kwargs: typing.Any,
) -> UniswapV3PoolMetadata:
    x_address, y_address = await async_get_pool_tokens(
        pool_address=pool_address
    )
    x_symbol, y_symbol = await evm.async_get_erc20s_symbols(
        tokens=[x_address, y_address], **rpc_kwargs
    )
    fee = await contracts.async_pool_fee(pool_address)
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
    start_block: spec.BlockNumberReference | None = None,
    end_block: spec.BlockNumberReference | None = None,
    replace_symbols: bool = False,
    normalize: bool = True,
) -> spec.DataFrame:

    if normalize or replace_symbols:
        metadata_task = asyncio.create_task(
            async_get_pool_metadata(pool_address)
        )

    event_abi = await uniswap_v3_spec.async_get_event_abi('Swap', 'pool')

    swaps = await evm.async_get_events(
        event_abi=event_abi,
        contract_address=pool_address,
        start_block=start_block,
        end_block=end_block,
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
    swaps = swaps.rename(columns=columns)

    # normalize columns
    if normalize:
        x_decimals, y_decimals = await evm.async_get_erc20s_decimals(
            tokens=[metadata['x_address'], metadata['y_address']],
        )
        swaps[columns['arg__amount0']] = swaps[columns['arg__amount0']].astype(
            float
        ) / (10 ** x_decimals)
        swaps[columns['arg__amount1']] = swaps[columns['arg__amount1']].astype(
            float
        ) / (10 ** y_decimals)

    return swaps

