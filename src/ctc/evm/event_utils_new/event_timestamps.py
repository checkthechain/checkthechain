from __future__ import annotations

import typing

from .. import block_utils
from ctc import spec


async def async_get_event_timestamps(
    events: spec.DataFrame,
    provider: spec.ProviderReference = None,
) -> typing.Sequence[int]:

    # get block_numbers
    multi_index = 'block_number' in events.index.names
    if multi_index:
        block_numbers = events.index.get_level_values('block_number')
    else:
        block_numbers = events.index.values

    # get timestamps
    return await block_utils.async_get_block_timestamps(
        block_numbers,
        provider=provider,
    )
