from __future__ import annotations

import typing

if typing.TYPE_CHECKING:
    import tooltime

import matplotlib.pyplot as plt  # type: ignore
import toolstr

from ctc import evm
from ctc import spec


if typing.TYPE_CHECKING:
    T = typing.TypeVar('T')


async def async_xtick_block_dates(
    provider: spec.ProviderReference = None,
) -> None:
    import tooltime

    start_block, end_block = plt.xlim()
    start_time, end_time = await evm.async_predict_block_timestamps(
        [round(start_block), round(end_block)], provider=provider
    )
    date_timestamps = tooltime.get_standard_intervals(
        interval_size='1d',
        start_time=start_time,
        end_time=end_time,
    )
    date_timestamps = [
        timestamp
        for timestamp in date_timestamps
        if timestamp >= start_time and timestamp <= end_time
    ]
    selected_dates = _select_interleaved(date_timestamps, 5)
    blocks_per_second = (end_block - start_block) / (end_time - start_time)
    locations = [
        start_block + blocks_per_second * (timestamp - start_time)
        for timestamp in selected_dates
    ]
    labels = [
        tooltime.convert_timestamp(timestamp, 'TimestampDate')
        for timestamp in selected_dates
    ]
    plt.xticks(locations, labels, ha='left', rotation=-25)


def _select_interleaved(
    items: typing.Sequence[T], number: int
) -> typing.Sequence[T]:
    import numpy as np

    if len(items) == 0:
        return []
    elif len(items) <= number:
        return items
    else:
        indices = np.linspace(0, len(items) - 1, number).round().astype(int)
        return [items[index] for index in indices]


async def async_block_timestamp_xticks(
    provider: spec.ProviderReference = None,
    representation: tooltime.TimestampExtendedRepresentation | None = None,
    *,
    omit: str | None = 'year',
) -> None:
    """
    matplotlib.FuncFormatter not used, because it cannot use async
    """

    raw_blocks, labels = plt.xticks()
    blocks = [int(block) for block in raw_blocks]
    block_timestamps = await evm.async_predict_block_timestamps(
        blocks, provider=provider
    )

    if representation is None:
        if len(block_timestamps) < 2:
            representation = 'TimestampDate'
        else:
            interval = block_timestamps[1] - block_timestamps[0]
            if interval > 86400:
                representation = 'TimestampDate'
            else:
                representation = 'TimestampISOPretty'

    labels = [
        toolstr.format(
            timestamp,
            format_type='timestamp',
            representation=representation,
        )
        for timestamp in block_timestamps
    ]

    # need to decide cleaner locations when dealing with shorter timescales
    # probably need to aim for somewhere between 4 and 6 ticks
    # should see how many ticks result from
    # - day intervals
    # - 12 hour intervals
    # - 6 hour intervals
    # - 4 hour intervals
    # - 3 hour intervals
    # - 2 hour intervals
    # - 1 hour intervals
    # - 30 minute intervals
    # - 20 minute intervals
    # - 10 minute intervals
    # - 5 minute intervals
    # - 2 minute intervals
    # - 1 minute intervals
    # - 30 second intervals
    # - 20 second intervals
    # - 10 second intervals
    # go for whichever size brings you closest to 5 ticks

    if representation == 'TimestampISOPretty' and omit is not None:
        if omit == 'year':
            labels = [label[5:] for label in labels]

    plt.xticks(raw_blocks, labels)
