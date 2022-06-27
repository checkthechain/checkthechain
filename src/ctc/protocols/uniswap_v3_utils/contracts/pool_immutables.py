from __future__ import annotations

from ctc import rpc
from ctc import spec

from .. import uniswap_v3_spec


async def async_pool_factory(
    pool: spec.Address,
    provider: spec.ProviderReference = None,
    block: spec.BlockNumberReference | None = None,
) -> spec.Address:
    function_abi = await uniswap_v3_spec.async_get_function_abi(
        'factory', 'pool'
    )
    return await rpc.async_eth_call(
        to_address=pool,
        function_abi=function_abi,
        provider=provider,
        block_number=block,
    )


async def async_pool_token0(
    pool: spec.Address,
    provider: spec.ProviderReference = None,
    block: spec.BlockNumberReference | None = None,
) -> spec.Address:
    function_abi = await uniswap_v3_spec.async_get_function_abi(
        'token0', 'pool'
    )
    return await rpc.async_eth_call(
        to_address=pool,
        function_abi=function_abi,
        provider=provider,
        block_number=block,
    )


async def async_pool_token1(
    pool: spec.Address,
    provider: spec.ProviderReference = None,
    block: spec.BlockNumberReference | None = None,
) -> spec.Address:
    function_abi = await uniswap_v3_spec.async_get_function_abi(
        'token1', 'pool'
    )
    return await rpc.async_eth_call(
        to_address=pool,
        function_abi=function_abi,
        provider=provider,
        block_number=block,
    )


async def async_pool_fee(
    pool: spec.Address,
    provider: spec.ProviderReference = None,
    block: spec.BlockNumberReference | None = None,
) -> int:
    function_abi = await uniswap_v3_spec.async_get_function_abi('fee', 'pool')
    return await rpc.async_eth_call(
        to_address=pool,
        function_abi=function_abi,
        provider=provider,
        block_number=block,
    )


async def async_pool_tick_spacing(
    pool: spec.Address,
    provider: spec.ProviderReference = None,
    block: spec.BlockNumberReference | None = None,
) -> int:
    function_abi = await uniswap_v3_spec.async_get_function_abi(
        'tickSpacing', 'pool'
    )
    return await rpc.async_eth_call(
        to_address=pool,
        function_abi=function_abi,
        provider=provider,
        block_number=block,
    )


async def async_pool_max_liquidity_per_tick(
    pool: spec.Address,
    provider: spec.ProviderReference = None,
    block: spec.BlockNumberReference | None = None,
) -> int:
    function_abi = await uniswap_v3_spec.async_get_function_abi(
        'maxLiquidityPerTick',
        'pool',
    )
    return await rpc.async_eth_call(
        to_address=pool,
        function_abi=function_abi,
        provider=provider,
        block_number=block,
    )

