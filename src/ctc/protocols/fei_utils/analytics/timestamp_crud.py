from __future__ import annotations

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
    timescale: typing.Optional[analytics_spec.TimescaleSpec] = None,
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
        timescale = resolve_timescale(timescale)
        if timestamps is None:
            if end_time is None:
                end_time = round(time.time())
            timestamps = get_timestamps(timescale=timescale, end_time=end_time)
        if blocks is None:
            blocks = await async_get_timestamps_blocks(
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


def resolve_timescale(
    timescale: analytics_spec.TimescaleSpec,
) -> analytics_spec.Timescale:
    if (
        isinstance(timescale, dict)
        and set(timescale.keys()) == {'window_size', 'interval_size'}
    ):
        return timescale

    elif isinstance(timescale, str) and timescale.count(',') == 1:
        window_size, interval_size = timescale.split(',')
        window_size = window_size.strip()
        interval_size = interval_size.strip()
        return {'window_size': window_size, 'interval_size': interval_size}

    else:
        raise Exception('could not resolve timescale: ' + str(timescale))


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


async def async_get_timestamps_blocks(
    timestamps: typing.Sequence[analytics_spec.Timestamp],
    provider: spec.ProviderSpec,
    **kwargs
) -> list[int]:

    # use latest block if last timestamp is greater than latest block timestamp
    latest_block = await evm.async_get_block('latest', provider=provider)
    if latest_block['timestamp'] <= timestamps[-1]:
        timestamps = timestamps[:-1]
        latest_block_swapped = True
    else:
        latest_block_swapped = False

    # allow only the last timestamp to exceed the latest block time
    for timestamp in timestamps:
        if timestamp > latest_block['timestamp']:
            raise Exception('timestamps are greater that latest block time')

    # get blocks of timestamps
    blocks = await evm.async_get_blocks_of_timestamps(
        timestamps, provider=provider, **kwargs
    )

    # append latest block if swapped in for last timestamp
    if latest_block_swapped:
        blocks.append(latest_block['number'])

    return blocks


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

