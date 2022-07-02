from __future__ import annotations

import typing

from ctc import spec
from ..analytics import analytics_spec
from ..analytics import timestamp_crud
from . import yields_spec
from . import yields_source_utils


async def async_create_fei_yield_payload(
    *,
    blocks: typing.Sequence[spec.BlockNumberReference] | None = None,
    timestamps: typing.Sequence[int] | None = None,
    timescale: analytics_spec.TimescaleSpec | None = None,
    end_time: analytics_spec.Timestamp | None = None,
    window_size: str | None = None,
    interval_size: str | None = None,
    provider: spec.ProviderReference = None,
) -> yields_spec.FeiYieldPayload:
    """create data payload from scratch"""

    time_data = await timestamp_crud.async_get_time_data(
        blocks=blocks,
        timestamps=timestamps,
        timescale=timescale,
        end_time=end_time,
        window_size=window_size,
        interval_size=interval_size,
        provider=provider,
    )

    # get data
    data = await yields_source_utils.async_get_fei_yield_data(
        block_numbers=time_data['block_numbers'],
    )

    return {
        'name': 'FEI Yield Data',
        'version': '0.1.0',
        #
        # time data
        'n_samples': time_data['n_samples'],
        'window_size': time_data['window_size'],
        'interval_size': time_data['interval_size'],
        'timestamps': time_data['timestamps'],
        'block_numbers': time_data['block_numbers'],
        'created_at_timestamp': time_data['created_at_timestamp'],
        #
        # metric data
        'data': data,
    }
