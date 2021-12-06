import time

from . import timestamp_crud
from . import metric_crud
from . import spec


async def async_create_payload(
    *,
    blocks=None,
    timestamps=None,
    timescale: spec.Timescale = None,
    end_time: spec.Timestamp = None,
) -> spec.AnalyticsPayload:
    """create data payload from scratch"""

    if blocks is None and timestamps is None:

        if timescale is None:
            raise Exception('must specify timescale or {blocks, timestamps}')

        if end_time is None:
            end_time = time.time()

        timestamps = timestamp_crud.get_timestamps(
            timescale=timescale, end_time=end_time
        )
        blocks = timestamp_crud.get_timestamps_blocks(timestamps=timestamps)

    metrics = await metric_crud.async_get_metrics(blocks=blocks)

    return {
        'version': '0.0',
        'timestamps': timestamps,
        'block_numbers': blocks,
        'metrics': metrics,
    }


def update_payload(
    timescale: spec.Timescale,
    old_payload: spec.AnalyticsPayload,
) -> spec.AnalyticsPayload:

    new_timestamps = get_new_timestamps(
        timescale=timescale,
        old_payload=old_payload,
    )
    new_blocks = get_new_blocks(
        new_timestamps=new_timestamps,
        old_payload=old_payload,
    )
    new_metrics = get_metrics(blocks=new_blocks)

    return combine_new_data(
        old_payload=old_payload,
        new_metrics=new_metrics,
    )

