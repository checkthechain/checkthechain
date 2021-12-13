import time
import typing

from . import timestamp_crud
from . import metric_crud
from . import analytics_spec


async def async_create_payload(
    *,
    blocks=None,
    timestamps=None,
    timescale: typing.Optional[analytics_spec.Timescale] = None,
    end_time: typing.Optional[analytics_spec.Timestamp] = None,
    window_size: str = None,
    interval_size: str = None,
) -> analytics_spec.AnalyticsPayload:
    """create data payload from scratch"""

    # parse missing inputs from timescale
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
            timestamps = timestamp_crud.get_timestamps(
                timescale=timescale, end_time=end_time
            )
        if blocks is None:
            blocks = timestamp_crud.get_timestamps_blocks(timestamps=timestamps)
        if interval_size is None:
            interval_size = timescale['interval_size']
        if window_size is None:
            window_size = timescale['window_size']

    metrics = await metric_crud.async_get_metrics(blocks=blocks)

    return {
        'version': '0.1.0',
        'timestamps': timestamps,
        'block_numbers': blocks,
        'n_samples': len(blocks),
        'window_size': window_size,
        'interval_size': interval_size,
        'created_at_timestamp': int(time.time()),
        'data': metrics,
    }


# def update_payload(
#     timescale: analytics_spec.Timescale,
#     old_payload: analytics_spec.AnalyticsPayload,
# ) -> analytics_spec.AnalyticsPayload:

#     new_timestamps = get_new_timestamps(
#         timescale=timescale,
#         old_payload=old_payload,
#     )
#     new_blocks = get_new_blocks(
#         new_timestamps=new_timestamps,
#         old_payload=old_payload,
#     )
#     new_metrics = get_metrics(blocks=new_blocks)

#     return combine_new_data(
#         old_payload=old_payload,
#         new_metrics=new_metrics,
#     )

