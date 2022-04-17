from __future__ import annotations

from ctc import rpc
from ctc import spec

from .. import uniswap_v3_spec


async def async_get_populated_ticks(
    pool: spec.Address,
    tick_bitmap_index: int,
) -> tuple[dict[str, int]]:
    function_abi = await uniswap_v3_spec.async_get_function_abi(
        'getPopulatedTicksInWord',
        'tick_lens',
    )
    return await rpc.async_eth_call(
        to_address=uniswap_v3_spec.tick_lens,
        function_abi=function_abi,
        function_parameters=[pool, tick_bitmap_index],
    )

