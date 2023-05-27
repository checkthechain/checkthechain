from __future__ import annotations

import typing

if typing.TYPE_CHECKING:
    import tooltime

from ctc import spec
from ... import block_crud
from . import block_time_search


async def async_get_block_of_timestamp(
    timestamp: tooltime.Timestamp,
    *,
    nary: typing.Optional[int] = None,
    cache: typing.Optional[block_time_search.BlockTimestampSearchCache] = None,
    block_timestamps: typing.Optional[typing.Mapping[int, int]] = None,
    block_timestamp_array: typing.Optional[spec.NumpyArray] = None,
    block_number_array: typing.Optional[spec.NumpyArray] = None,
    verbose: bool = False,
    context: spec.Context = None,
    mode: typing.Literal['<=', '>=', '=='] = '>=',
) -> int:
    """search for the block that corresponds to a given timestamp"""

    if not isinstance(timestamp, int):
        import tooltime

        timestamp = tooltime.timestamp_to_seconds(timestamp)

    if block_timestamps is not None or (
        block_timestamp_array is not None and block_number_array is not None
    ):
        return _get_block_of_timestamp_from_arrays(
            timestamp=timestamp,
            block_timestamp_array=block_timestamp_array,
            block_number_array=block_number_array,
            block_timestamps=block_timestamps,
            verbose=verbose,
        )
    else:

        from ctc import config

        # db
        read_cache, write_cache = config.get_context_cache_read_write(
            schema_name='block_timestamps', context=context
        )
        if read_cache:
            from ctc import db

            block = await db.async_query_timestamp_block(
                timestamp=timestamp,
                mode=mode,
                context=context,
            )
            if block is not None:
                return block

        # rpc node
        return await block_time_search._async_get_block_of_timestamp_from_node(
            timestamp=timestamp,
            nary=nary,
            cache=cache,
            verbose=verbose,
            context=context,
            mode=mode,
        )


def _get_block_of_timestamp_from_arrays(
    timestamp: tooltime.Timestamp,
    *,
    block_timestamp_array: spec.NumpyArray | None = None,
    block_number_array: spec.NumpyArray | None = None,
    block_timestamps: typing.Mapping[int, int] | None = None,
    verbose: bool = False,
) -> int:
    import numpy as np

    if block_timestamp_array is None:
        if block_timestamps is None:
            raise Exception('must specify more arguments')
        block_timestamp_array = np.array(list(block_timestamps.values()))
    if block_number_array is None:
        if block_timestamps is None:
            raise Exception('must specify more arguments')
        block_number_array = np.array(list(block_timestamps.keys()))

    if not isinstance(timestamp, int):
        import tooltime

        timestamp = tooltime.timestamp_to_seconds(timestamp)

    index = np.searchsorted(block_timestamp_array, timestamp)
    result = block_number_array[index]
    if not isinstance(result, int):
        raise Exception('invalid rpc result')
    return result


async def async_get_block_number_and_time(
    *,
    block_number: typing.Optional[spec.BlockNumberReference] = None,
    block_timestamp: typing.Optional[tooltime.Timestamp] = None,
    context: spec.Context = None,
) -> tuple[int, int]:
    """get block number and timestamp corresponding to given input"""

    if block_timestamp is not None and block_number is not None:
        raise Exception('must specify start_time or block_number')

    if block_number is not None:
        block = await block_crud.async_get_block(
            block_number, context=context
        )
        return block['number'], block['timestamp']

    elif block_timestamp is not None:
        block_number = await async_get_block_of_timestamp(
            block_timestamp, context=context
        )
        block = await block_crud.async_get_block(
            block_number, context=context
        )
        return block['number'], block['timestamp']

    else:
        raise Exception('must specify start_time or block_number')
