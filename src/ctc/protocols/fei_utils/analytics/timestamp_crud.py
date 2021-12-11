import time
import typing

import toolstr
import tooltime

from ctc import evm
from . import analytics_spec


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


def get_timestamps_blocks(timestamps: analytics_spec.Timestamps, **kwargs) -> list[int]:
    return evm.get_blocks_of_timestamps(timestamps, **kwargs)


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

