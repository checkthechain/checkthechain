from __future__ import annotations

import typing

from ctc import spec
from .. import block_crud
from . import block_to_timestamp
from . import timestamp_to_block

if typing.TYPE_CHECKING:
    import tooltime


async def async_sample_blocks(
    *,
    start_block: spec.BlockNumberReference | None = None,
    end_block: spec.BlockNumberReference | None = None,
    include_latest_if_trimmed: bool = True,
    start_time: tooltime.Timestamp | None = None,
    end_time: tooltime.Timestamp | None = None,
    n_samples: int | None = None,
    sample_interval: tooltime.Timelength | None = None,
    window_size: tooltime.Timelength | None = None,
    align_to: typing.Literal['start', 'end'] = 'start',
    include_misaligned_bound: bool = False,
    include_misaligned_overflow: bool = False,
) -> typing.Sequence[int]:
    """create sample of blocks matching input sampling parameters"""

    import tooltime

    if start_block is not None:
        start_time = await block_to_timestamp.async_get_block_timestamp(
            start_block
        )
    if end_block is not None:
        end_time = await block_to_timestamp.async_get_block_timestamp(end_block)

    float_timestamps = tooltime.sample_timestamps(
        start_time=start_time,
        end_time=end_time,
        n_samples=n_samples,
        sample_interval=sample_interval,
        window_size=window_size,
        align_to=align_to,
        include_misaligned_bound=include_misaligned_bound,
        include_misaligned_overflow=include_misaligned_overflow,
    )
    timestamps: typing.Sequence[int] = [
        round(timestamp) for timestamp in float_timestamps
    ]

    # time to latest block timestamp
    latest_block = await block_crud.async_get_block('latest')
    latest_block_timestamp = latest_block['timestamp']
    n_original_timestamps = len(timestamps)
    timestamps = [
        timestamp
        for timestamp in timestamps
        if timestamp <= latest_block_timestamp
    ]
    trimmed = len(timestamps) != n_original_timestamps

    # get blocks of timestamps
    blocks = await timestamp_to_block.async_get_blocks_of_timestamps(
        timestamps=timestamps,
    )

    # include latest if trimmed
    if trimmed and include_latest_if_trimmed:
        latest_block_number = latest_block['number']
        if blocks[-1] != latest_block_number:
            blocks.append(latest_block_number)

    return blocks
