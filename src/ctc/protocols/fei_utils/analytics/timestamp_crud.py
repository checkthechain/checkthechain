import time
import typing

import toolstr
import tooltime

from ctc import evm
from ctc import spec
from . import analytics_spec


async def async_get_time_data(
    blocks: typing.Sequence[spec.BlockNumberReference] = None,
    timestamps: typing.Sequence[int] = None,
    timescale: typing.Optional[analytics_spec.Timescale] = None,
    end_time: typing.Optional[analytics_spec.Timestamp] = None,
    window_size: str = None,
    interval_size: str = None,
    provider: spec.ProviderSpec = None,
) -> analytics_spec.TimeData:

    if (
        blocks is None
        or timestamps is None
        or window_size is None
        or interval_size is None
    ):
        if timescale is None:
            raise Exception('must specify timescale or {blocks, timestamps}')
        if timestamps is None:
            if end_time is None:
                end_time = round(time.time())
            timestamps = get_timestamps(timescale=timescale, end_time=end_time)
        if blocks is None:
            blocks = get_timestamps_blocks(
                timestamps=timestamps, provider=provider
            )
        if interval_size is None:
            interval_size = timescale['interval_size']
        if window_size is None:
            window_size = timescale['window_size']

    timestamps = list(timestamps)
    blocks = await evm.async_block_numbers_to_int(
        blocks=blocks, provider=provider
    )

    return {
        'timestamps': timestamps,
        'block_numbers': blocks,
        'n_samples': len(blocks),
        'window_size': window_size,
        'interval_size': interval_size,
        'created_at_timestamp': int(time.time()),
    }


def get_timestamps(
    timescale: analytics_spec.Timescale,
    end_time: typing.Optional[analytics_spec.Timestamp] = None,
) -> analytics_spec.Timestamps:

    if end_time is None:
        end_time = int(time.time())

    return tooltime.get_standard_intervals(
        interval_size=timescale['interval_size'],
        window_size=timescale['window_size'],
        end_time=end_time,
    )


def get_timestamps_blocks(
    timestamps: typing.Sequence[analytics_spec.Timestamp],
    provider: spec.ProviderSpec,
    **kwargs
) -> list[int]:
    return evm.get_blocks_of_timestamps(timestamps, provider=provider, **kwargs)


def summarize_timestamps(
    timescale: analytics_spec.Timescale,
    timestamps: analytics_spec.Timestamps,
) -> None:
    toolstr.print_text_box(
        'window = '
        + tooltime.timelength_to_phrase(timescale['window_size'])
        + ', precision = '
        + tooltime.timelength_to_phrase(timescale['interval_size'])
        + ', n_points = '
        + str(len(timestamps))
    )
    n_show = 2
    if len(timestamps) > n_show * 2:
        for timestamp in timestamps[:n_show]:
            print('   ', tooltime.timestamp_to_iso(timestamp))
        print('   ', '...')
        for timestamp in timestamps[-n_show:]:
            print('   ', tooltime.timestamp_to_iso(timestamp))
    else:
        for timestamp in timestamps:
            print('   ', tooltime.timestamp_to_iso(timestamp))
    print()
    print()

