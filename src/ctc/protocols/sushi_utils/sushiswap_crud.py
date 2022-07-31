from __future__ import annotations

import typing

from ctc.protocols import uniswap_v2_utils
from ctc import spec

if typing.TYPE_CHECKING:
    import tooltime


async def async_get_pool_swaps(
    pool_address: spec.Address,
    *,
    start_block: spec.BlockNumberReference | None = None,
    end_block: spec.BlockNumberReference | None = None,
    start_time: tooltime.Timestamp | None = None,
    end_time: tooltime.Timestamp | None = None,
    replace_symbols: bool = False,
    normalize: bool = True,
) -> spec.DataFrame:
    return await uniswap_v2_utils.async_get_pool_swaps(
        pool_address=pool_address,
        start_block=start_block,
        end_block=end_block,
        start_time=start_time,
        end_time=end_time,
        replace_symbols=replace_symbols,
        normalize=normalize,
    )
