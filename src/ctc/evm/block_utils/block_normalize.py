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


async def async_block_reference_to_int(
    block: spec.BlockReference,
    *,
    context: spec.Context,
) -> int:
    """convert block number, block hash, or block name to int"""
    if spec.is_block_number_reference(block):
        return await async_block_number_to_int(block, context=context)
    elif spec.is_block_hash(block):
        import ctc.rpc

        block_data: spec.RPCBlock = await ctc.rpc.async_eth_get_block_by_hash(
            block, context=context
        )
        return block_data['number']
    else:
        raise Exception('unknown block format: ' + str(block))


async def async_block_references_to_int(
    blocks: typing.Sequence[spec.BlockReference],
    *,
    context: spec.Context,
) -> typing.Sequence[int]:
    """convert block number, block hash, or block name to int"""
    import asyncio

    coroutines = [
        async_block_reference_to_int(block=block, context=context)
        for block in blocks
    ]
    return await asyncio.gather(*coroutines)

