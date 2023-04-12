from __future__ import annotations

import typing

from ctc import spec

if typing.TYPE_CHECKING:
    import tooltime


async def async_get_block_intervals(
    interval_size: tooltime.Timelength,
    *,
    start_time: typing.Optional[tooltime.Timestamp] = None,
    end_time: typing.Optional[tooltime.Timestamp] = None,
    n_intervals: typing.Optional[int] = None,
    window_size: typing.Optional[tooltime.Timelength] = None,
    blocks_at: typing.Literal['start', 'middle', 'end'] = 'middle',
    context: spec.Context | None = None,
    contexts: typing.Sequence[spec.Context] | spec.Context | None = None,
    prefix_network: bool | None = None,
) -> spec.DataFrame:
    """return DataFrame of time intervals with block numbers and timestamps"""

    import asyncio
    import ctc.config
    import tooltime
    import polars as pl

    df = tooltime.get_interval_df(
        interval_size=interval_size,
        start_time=start_time,
        end_time=end_time,
        n_intervals=n_intervals,
        window_size=window_size,
    )

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

