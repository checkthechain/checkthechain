from __future__ import annotations

import typing

import ctc
from ctc import spec

if typing.TYPE_CHECKING:
    import tooltime


async def async_get_block_intervals(
    interval_size: tooltime.Timelength,
    *,
    start_time: tooltime.Timestamp | None = None,
    end_time: tooltime.Timestamp | None = None,
    start_block: spec.BlockNumberReference | None = None,
    end_block: spec.BlockNumberReference | None = None,
    n_intervals: int | None = None,
    window_size: tooltime.Timelength | None = None,
    blocks_at: typing.Literal['start', 'middle', 'end'] = 'middle',
    context: spec.Context | None = None,
    contexts: typing.Sequence[spec.Context] | spec.Context | None = None,
    prefix_network: bool | None = None,
) -> spec.DataFrame:
    """return DataFrame of time intervals with block numbers and timestamps

    TODO: adapt features of async_sample_blocks() below into this function
    """

    import asyncio
    import ctc.config
    import tooltime
    import polars as pl

    # organize contexts
    if contexts is None:
        contexts = [context]
    elif isinstance(contexts, dict):
        contexts = [contexts]
    elif isinstance(contexts, list):
        if len(contexts) == 0:
            contexts = [context]
    else:
        raise Exception("unknown contexts format: " + str(type(contexts)))

    if start_block is not None:
        if len(contexts) != 1:
            raise Exception('invalid context for using start_block')
        start_time = await ctc.async_get_block_timestamp(
            start_block,
            context=contexts[0],
        )
    if end_block is not None:
        if len(contexts) != 1:
            raise Exception('invalid context for using end_block')
        end_time = await ctc.async_get_block_timestamp(
            end_block,
            context=contexts[0],
        )

    df = tooltime.get_interval_df(
        interval_size=interval_size,
        start_time=start_time,
        end_time=end_time,
        n_intervals=n_intervals,
        window_size=window_size,
    )

    # get blocks
    if blocks_at == 'start':
        timestamps = df['start_timestamp']
    elif blocks_at == 'end':
        timestamps = df['end_timestamp']
    elif blocks_at == 'middle':
        timestamps = df['middle_timestamp']
    else:
        raise Exception()

    # get column names
    if prefix_network is None:
        prefix_network = len(contexts) > 1
    if not prefix_network and len(contexts) > 1:
        raise Exception(
            'you must use prefix_network when using multiple contexts'
        )
    if prefix_network:
        names = [
            ctc.config.get_context_network_name(context) + '_block'
            for context in contexts
        ]
    else:
        names = ['block']

    # gather block numbers
    coroutines = [
        ctc.async_get_blocks_of_timestamps(
            timestamps.to_list(), context=context
        )
        for context in contexts
    ]
    contexts_blocks = await asyncio.gather(*coroutines)

    # create dataframe
    block_df = pl.DataFrame(dict(zip(names, contexts_blocks)))
    return df.with_columns(block_df)

# async def async_sample_blocks(
#     *,
#     start_block: spec.BlockNumberReference | None = None,
#     end_block: spec.BlockNumberReference | None = None,
#     include_latest_if_trimmed: bool = True,
#     start_time: tooltime.Timestamp | None = None,
#     end_time: tooltime.Timestamp | None = None,
#     n_samples: int | None = None,
#     sample_interval: tooltime.Timelength | None = None,
#     window_size: tooltime.Timelength | None = None,
#     align_to: typing.Literal['start', 'end'] = 'start',
#     include_misaligned_bound: bool = False,
#     include_misaligned_overflow: bool = False,
#     context: spec.Context = None,
# ) -> typing.Sequence[int]:
#     """create sample of blocks matching input sampling parameters"""

#     import tooltime

#     if start_block is not None:
#         start_time = await block_to_timestamp.async_get_block_timestamp(
#             start_block,
#             context=context,
#         )
#     if end_block is not None:
#         end_time = await block_to_timestamp.async_get_block_timestamp(
#             end_block, context=context
#         )

#     float_timestamps = tooltime.sample_timestamps(
#         start_time=start_time,
#         end_time=end_time,
#         n_samples=n_samples,
#         sample_interval=sample_interval,
#         window_size=window_size,
#         align_to=align_to,
#         include_misaligned_bound=include_misaligned_bound,
#         include_misaligned_overflow=include_misaligned_overflow,
#     )
#     timestamps: typing.Sequence[int] = [
#         round(timestamp) for timestamp in float_timestamps
#     ]

#     # time to latest block timestamp
#     latest_block = await block_crud.async_get_block('latest', context=context)
#     latest_block_timestamp = latest_block['timestamp']
#     n_original_timestamps = len(timestamps)
#     timestamps = [
#         timestamp
#         for timestamp in timestamps
#         if timestamp <= latest_block_timestamp
#     ]
#     trimmed = len(timestamps) != n_original_timestamps

#     # get blocks of timestamps
#     blocks = await timestamp_to_block.async_get_blocks_of_timestamps(
#         timestamps=timestamps, context=context
#     )

#     # include latest if trimmed
#     if trimmed and include_latest_if_trimmed:
#         latest_block_number = latest_block['number']
#         if blocks[-1] != latest_block_number:
#             blocks.append(latest_block_number)

#     return blocks

