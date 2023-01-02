from __future__ import annotations

import typing

from ctc import spec
from . import block_time_search
from . import block_time_singular

if typing.TYPE_CHECKING:
    from typing_extensions import Literal


async def async_get_blocks_of_timestamps(
    timestamps: typing.Sequence[int],
    *,
    block_timestamps: typing.Mapping[int, int] | None = None,
    block_number_array: spec.NumpyArray | None = None,
    block_timestamp_array: spec.NumpyArray | None = None,
    nary: int | None = None,
    cache: block_time_search.BlockTimestampSearchCache | None = None,
    mode: Literal['<=', '>=', '=='] = '>=',
    context: spec.Context = None,
) -> list[int]:
    """search for blocks corresponding to list of timestamps"""

    from ctc import config

    read_cache, write_cache = config.get_context_cache_read_write(
        schema_name='block_timestamps', context=context
    )

    if block_timestamps is not None or (
        block_number_array is not None and block_timestamp_array is not None
    ):
        import numpy as np

        if mode != '>=':
            raise NotImplementedError()

        if block_timestamp_array is None:
            if block_timestamps is None:
                raise Exception('must specify more arguments')
            block_timestamp_array = np.array(list(block_timestamps.values()))
        if block_number_array is None:
            if block_timestamps is None:
                raise Exception('must specify more arguments')
            block_number_array = np.array(list(block_timestamps.keys()))

        blocks = []
        for timestamp in timestamps:
            block = block_time_singular._get_block_of_timestamp_from_arrays(
                timestamp=timestamp,
                block_timestamp_array=block_timestamp_array,
                block_number_array=block_number_array,
                verbose=False,
            )
            blocks.append(block)

        return blocks

    else:

        # get timestamps form db
        if read_cache:
            from ctc import db

            db_blocks = await db.async_query_timestamps_blocks(
                context=context,
                timestamps=timestamps,
                mode=mode,
            )
            if db_blocks is None:
                db_blocks = [None for timestamp in timestamps]

            # package non-null results
            results: dict[int, int] = {}
            remaining_timestamps: list[int] = []
            for possible_block, timestamp in zip(db_blocks, timestamps):
                if possible_block is None:
                    remaining_timestamps.append(timestamp)
                else:
                    results[timestamp] = possible_block
        else:
            remaining_timestamps = list(timestamps)
            results = {}

        # get timestamps from rpc node
        if len(remaining_timestamps) > 0:
            coroutines = []
            for timestamp in remaining_timestamps:
                coroutine = block_time_singular.async_get_block_of_timestamp(
                    timestamp=timestamp,
                    verbose=False,
                    cache=cache,
                    nary=nary,
                    context=config.update_context(context=context, cache=False),
                    mode=mode,
                )
                coroutines.append(coroutine)
            import asyncio

            node_blocks = await asyncio.gather(*coroutines)
            node_results = dict(zip(remaining_timestamps, node_blocks))
            results.update(node_results)

        # combine
        return [results[timestamp] for timestamp in timestamps]
