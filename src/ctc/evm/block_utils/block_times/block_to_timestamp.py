from __future__ import annotations

import typing

from ctc import spec

from .. import block_crud
from .. import block_normalize


async def async_get_block_timestamp(
    block: spec.BlockReference,
    *,
    context: spec.Context = None,
) -> int:
    """get timestamp of block"""

    from ctc import config

    read_cache, write_cache = config.get_context_cache_read_write(
        schema_name='block_timestamps', context=context
    )
    if isinstance(block, int) and read_cache:
        from ctc import db

        timestamp = await db.async_query_block_timestamp(
            block_number=block,
            context=context,
        )
        if timestamp is not None:
            return timestamp

    block_data = await block_crud.async_get_block(block, context=context)
    return block_data['timestamp']


async def async_get_block_timestamps(
    blocks: typing.Sequence[spec.BlockReference],
    *,
    context: spec.Context = None,
) -> list[int]:
    """get timestamps of blocks"""

    from ctc import config

    blocks = await block_normalize.async_block_numbers_to_int(
        blocks=blocks,
        context=context,
    )

    # get timestamps from db
    read_cache, write_cache = config.get_context_cache_read_write(
        schema_name='block_timestamps', context=context
    )
    if read_cache:
        from ctc import db

        db_timestamps = await db.async_query_block_timestamps(
            block_numbers=blocks,
            context=context,
        )
        if db_timestamps is None:
            db_timestamps = [None for block in blocks]
        results: dict[int, int | None] = dict(zip(blocks, db_timestamps))
        remaining_blocks: typing.Sequence[int] = [
            block
            for block, timestamp in zip(blocks, db_timestamps)
            if timestamp is None
        ]
    else:
        results = {}
        remaining_blocks = blocks

    # get timestamps from rpc
    if len(remaining_blocks) > 0:
        node_blocks = await block_crud.async_get_blocks(
            blocks=remaining_blocks,
            context=context,
        )
        for block_data in node_blocks:
            results[block_data['number']] = block_data['timestamp']

    output: list[int] = []
    for block in blocks:
        result = results[block]
        if result is None:
            raise Exception('failed to get timestamp for block: ' + str(block))
        output.append(result)
    return output
