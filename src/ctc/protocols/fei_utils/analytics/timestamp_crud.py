import time

import toolstr
import tooltime

from ctc import evm
from . import spec


def get_timestamps(
    timescale: spec.Timescale,
    end_time: spec.Timestamp = None,
) -> spec.Timestamps:

    if end_time is None:
        end_time = time.time()

    return tooltime.get_standard_intervals(
        interval_size=timescale['interval_size'],
        window_size=timescale['window_size'],
        end_time=end_time,
    )


def get_timestamps_blocks(timestamps: spec.Timestamps, **kwargs) -> list[int]:
    return evm.get_blocks_of_timestamps(timestamps, **kwargs)


def summarize_timestamps(
    timescale: spec.Timescale,
    timestamps: spec.Timestamps,
) -> list[int]:
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

