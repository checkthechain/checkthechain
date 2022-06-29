from __future__ import annotations

import os
import typing

from ctc import spec


block_timestamps_template = (
    'block_timestamps__{start_block}_to_{end_block}__{t_index}_{t_start}.npz'
)


def save_compressed_block_timestamps(
    block_timestamps: typing.Mapping[int, int],
    *,
    dirname: str | None = None,
    path: str | None = None,
    clip_t0: bool | None = None,
) -> str:
    import numpy as np

    start_block = min(block_timestamps.keys())
    end_block = max(block_timestamps.keys())

    timestamps = []
    for i in range(start_block, end_block + 1):
        timestamps.append(block_timestamps[i])

    # clip t0 if need be
    if clip_t0 is None:
        clip_t0 = block_timestamps[start_block] == 0
    if clip_t0:
        timestamps = timestamps[1:]
        t_index = 't1'
    else:
        t_index = 't0'
    t_start = timestamps[0]

    # compute diffs
    timestamps_array: spec.NumpyArray = np.array(timestamps)
    timestamp_diffs = timestamps_array[1:] - timestamps_array[:-1]

    # convert to efficient dtype
    dtype: type = np.int16
    if (timestamp_diffs > np.iinfo(dtype).max).sum() > 0:
        dtype = np.int32
    timestamp_diffs = timestamp_diffs.astype(dtype)

    if path is None:
        filename = block_timestamps_template.format(
            start_block=start_block,
            end_block=end_block,
            t_index=t_index,
            t_start=t_start,
        )
        if dirname is not None:
            path = os.path.join(dirname, filename)
        else:
            path = filename

    np.savez_compressed(path, timestamp_diffs=timestamp_diffs)

    return path


def load_compressed_block_times(
    path: str,
    *,
    start_block: int | None = None,
    end_block: int | None = None,
    t0: int | None = None,
    t1: int | None = None,
) -> typing.Mapping[int, int]:

    import numpy as np

    if start_block is None or end_block is None or (t0 is None and t1 is None):
        filename = os.path.basename(path)
        name = os.path.splitext(filename)[0]
        _, block_range, t_info = name.split('__')

        start_block_str, end_block_str = block_range.split('_to_')
        start_block = int(start_block_str)
        end_block = int(end_block_str)

        t_index, t_str = t_info.split('_')
        t_start = int(t_str)

    timestamp_diffs = np.load(path)['timestamp_diffs']

    if t_index == 't0':
        head = [t_start]
    elif t_index == 't1':
        head = [0, t_start]
    else:
        raise Exception()
    tail = [int(item) for item in (t_start + np.cumsum(timestamp_diffs))]
    timestamps = head + tail

    blocks = range(start_block, end_block + 1)
    return dict(zip(blocks, timestamps))
