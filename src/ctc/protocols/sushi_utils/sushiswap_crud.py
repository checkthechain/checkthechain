
from ctc.protocols import uniswap_v2_utils


async def async_get_pool_swaps(
    pool_address,
    start_block=None,
    end_block=None,
    replace_symbols=False,
    normalize=True,
):
    return await uniswap_v2_utils.async_get_pool_swaps(
        pool_address=pool_address,
        start_block=start_block,
        end_block=end_block,
        replace_symbols=replace_symbols,
        normalize=normalize,
    )

