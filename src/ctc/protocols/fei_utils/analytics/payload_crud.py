import typing

from ctc import spec
from . import timestamp_crud
from . import metric_crud
from . import analytics_spec


async def async_create_payload(
    *,
    blocks: typing.Sequence[spec.BlockNumberReference] = None,
    timestamps: typing.Sequence[int] = None,
    timescale: typing.Optional[analytics_spec.TimescaleSpec] = None,
    end_time: typing.Optional[analytics_spec.Timestamp] = None,
    window_size: str = None,
    interval_size: str = None,
    provider: spec.ProviderSpec = None,
) -> analytics_spec.AnalyticsPayload:
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
    data = await metric_crud.async_get_metrics(
        blocks=time_data['block_numbers']
    )

    return {
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

