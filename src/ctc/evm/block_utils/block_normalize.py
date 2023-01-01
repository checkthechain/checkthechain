from __future__ import annotations

import typing

from ctc import evm
from ctc import spec
from . import block_crud


async def async_block_number_to_int(
    block: spec.BlockNumberReference,
    *,
    context: spec.Context = None,
) -> int:
    """resolve block number reference to int (e.g. converting 'latest' to int)

    Examples: 'latest', or 9999.0, or 9999
    """
    if block is None:
        block = 'latest'
    if block in spec.block_number_names:
        return await block_crud.async_get_latest_block_number(context=context)
    else:
        return evm.raw_block_number_to_int(block)


async def async_block_numbers_to_int(
    blocks: typing.Sequence[spec.BlockNumberReference],
    *,
    context: spec.Context = None,
) -> typing.Sequence[int]:
    """convert block numers to integer"""

    import asyncio

    coroutines = [
        async_block_number_to_int(block=block, context=context)
        for block in blocks
    ]
    return await asyncio.gather(*coroutines)

