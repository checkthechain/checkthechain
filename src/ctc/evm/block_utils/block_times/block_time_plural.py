from __future__ import annotations

import asyncio
import typing

from ctc import spec

from . import block_time_search
from . import block_time_singular


async def async_get_blocks_of_timestamps(
    timestamps: typing.Sequence[int],
    block_timestamps: typing.Optional[typing.Mapping[int, int]] = None,
    block_number_array: typing.Optional[spec.NumpyArray] = None,
    block_timestamp_array: typing.Optional[spec.NumpyArray] = None,
    nary: typing.Optional[int] = None,
    cache: typing.Optional[block_time_search.BlockTimestampSearchCache] = None,
    provider: spec.ProviderSpec = None,
) -> list[int]:
    """once parallel node search created, use that"""

    if block_timestamps is not None or (
        block_number_array is not None and block_timestamp_array is not None
    ):
        import numpy as np

        if block_timestamp_array is None:
            if block_timestamps is None:
                raise Exception('must specify more arguments')
            block_timestamp_array = np.array(list(block_timestamps.values()))
        if block_number_array is None:
            if block_timestamps is None:
                raise Exception('must specify more arguments')
            block_number_array = np.array(list(block_timestamps.keys()))

        blocks = []
        for timestamp in timestamps:
            block = block_time_singular.get_block_of_timestamp_from_arrays(
                timestamp=timestamp,
                block_timestamp_array=block_timestamp_array,
                block_number_array=block_number_array,
                verbose=False,
            )
            blocks.append(block)

        return blocks

    else:

        coroutines = []
        for timestamp in timestamps:
            coroutine = block_time_singular.async_get_block_of_timestamp(
                timestamp=timestamp,
                verbose=False,
                cache=cache,
                nary=nary,
                provider=provider,
            )
            coroutines.append(coroutine)

        return await asyncio.gather(*coroutines)

