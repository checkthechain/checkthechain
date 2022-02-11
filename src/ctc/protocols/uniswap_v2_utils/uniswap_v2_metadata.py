from __future__ import annotations

import asyncio

from ctc import evm
from ctc import rpc
from ctc import spec

from . import uniswap_v2_spec


async def async_get_pool_tokens(
    pool: spec.Address,
    provider: spec.ProviderSpec = None,
) -> tuple[spec.Address, spec.Address]:

    token0 = rpc.async_eth_call(
        function_name='token0', to_address=pool, provider=provider
    )
    token1 = rpc.async_eth_call(
        function_name='token1', to_address=pool, provider=provider
    )

    return await asyncio.gather(token0, token1)


async def async_get_pool_symbols(
    pool: spec.Address = None,
    *,
    x_address: spec.Address = None,
    y_address: spec.Address = None,
    provider: spec.ProviderSpec = None,
):

    if x_address is None or y_address is None:
        if pool is None:
            raise Exception('must specify pool or tokens')
        x_address, y_address = await async_get_pool_tokens(
            pool=pool, provider=provider
        )

    return await evm.async_get_erc20s_symbols(
        tokens=[x_address, y_address],
        provider=provider,
    )


async def async_get_pool_decimals(
    pool: spec.Address = None,
    *,
    x_address: spec.Address = None,
    y_address: spec.Address = None,
    provider: spec.ProviderSpec = None,
):

    if x_address is None or y_address is None:
        if pool is None:
            raise Exception('must specify pool or tokens')
        x_address, y_address = await async_get_pool_tokens(
            pool=pool, provider=provider
        )

    return await evm.async_get_erc20s_decimals(
        tokens=[x_address, y_address],
        provider=provider,
    )


async def async_get_pool_tokens_metadata(
    pool: spec.Address,
    provider: spec.ProviderSpec = None,
) -> uniswap_v2_spec.PoolTokensMetadata:

    x_address, y_address = await async_get_pool_tokens(
        pool=pool,
        provider=provider,
    )

    symbols_coroutine = async_get_pool_symbols(
        x_address=x_address,
        y_address=y_address,
        provider=provider,
    )

    decimals_coroutine = async_get_pool_decimals(
        x_address=x_address,
        y_address=y_address,
        provider=provider,
    )

    symbols, decimals = await asyncio.gather(
        symbols_coroutine, decimals_coroutine
    )
    x_symbol, y_symbol = symbols
    x_decimals, y_decimals = decimals

    return {
        'x_address': x_address,
        'y_address': y_address,
        'x_symbol': x_symbol,
        'y_symbol': y_symbol,
        'x_decimals': x_decimals,
        'y_decimals': y_decimals,
    }

