from __future__ import annotations

import typing

from ctc import rpc
from ctc import spec

from .. import uniswap_v3_spec


async def async_get_populated_ticks(
    pool: spec.Address,
    tick_bitmap_index: int,
) -> tuple[typing.Mapping[str, int], ...]:
    function_abi = await uniswap_v3_spec.async_get_function_abi(
        'getPopulatedTicksInWord',
        'tick_lens',
    )
    result = await rpc.async_eth_call(
        to_address=uniswap_v3_spec.tick_lens,
        function_abi=function_abi,
        function_parameters=[pool, tick_bitmap_index],
    )
    if not isinstance(result, tuple) or not all(
        isinstance(item, dict) for item in result
    ):
        raise Exception('invalid rpc result')
    return typing.cast(typing.Tuple[typing.Mapping[str, int], ...], result)
