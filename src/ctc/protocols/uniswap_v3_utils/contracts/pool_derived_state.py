from __future__ import annotations

from ctc import rpc
from ctc import spec

from .. import uniswap_v3_spec


async def async_pool_observe(
    seconds_agos: list[int],
    pool: spec.Address,
    *,
    provider: spec.ProviderReference = None,
    block: spec.BlockNumberReference | None = None,
) -> dict[str, int]:
    function_abi = await uniswap_v3_spec.async_get_function_abi(
        'observe', 'pool'
    )
    result = await rpc.async_eth_call(
        to_address=pool,
        function_abi=function_abi,
        function_parameters=[seconds_agos],
        provider=provider,
        block_number=block,
    )
    return {
        'tick_cumulatives': result[0],
        'seconds_per_liquidity_cumulative_x128': result[1],
    }


async def async_pool_snapshot_cumulatives_inside(
    *,
    tick_lower: int,
    tick_upper: int,
    pool: spec.Address,
    provider: spec.ProviderReference = None,
    block: spec.BlockNumberReference | None = None,
) -> dict[str, int]:
    function_abi = await uniswap_v3_spec.async_get_function_abi(
        'snapshotCumulativesInside',
        'pool',
    )
    result = await rpc.async_eth_call(
        to_address=pool,
        function_abi=function_abi,
        function_parameters=[tick_lower, tick_upper],
        provider=provider,
        block_number=block,
    )
    return {
        'tick_cumulative_inside': result[0],
        'seconds_per_liquidity_x128': result[1],
        'seconds_inside': result[2],
    }
