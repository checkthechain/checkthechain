from ctc import rpc

from .. import uniswap_v3_spec


async def async_get_populated_ticks(pool, tick_bitmap_index):
    function_abi = await uniswap_v3_spec.get_function_abi(
        'getPopulatedTicksInWord',
        'tick_lens',
    )
    return await rpc.async_eth_call(
        to_address=uniswap_v3_spec.tick_lens,
        function_abi=function_abi,
        function_parameters=[pool, tick_bitmap_index],
    )

