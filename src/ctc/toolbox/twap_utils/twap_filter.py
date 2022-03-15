from __future__ import annotations

import typing

import tooltime

from ctc import spec


def filter_twap(
    raw_values: typing.Sequence,
    timestamps: typing.Sequence,
    filter_duration: tooltime.Timestamp,
) -> spec.Series:
    """convert raw value of a TWAP"""

    import numpy as np
    import pandas as pd

    # compute twap times
    timestamps = np.array(timestamps)
    filter_seconds = tooltime.timestamp_to_seconds(filter_duration)
    first_input_timestamp = timestamps[0]
    output_mask = timestamps > first_input_timestamp + filter_seconds
    twap_times = timestamps[output_mask]

    # compute twap values
    # cannot use efficient numpy operation because filter size is variable
    # (because block times are variable)
    raw_values = np.array(raw_values)
    twap_values = []
    for twap_time in twap_times:
        lower_bound = twap_time - filter_seconds < timestamps
        upper_bound = timestamps <= twap_time
        block_mask = lower_bound * upper_bound
        twap_value = raw_values[block_mask].mean()
        twap_values.append(twap_value)

    # format as Series
    return pd.Series(twap_values, index=twap_times)

