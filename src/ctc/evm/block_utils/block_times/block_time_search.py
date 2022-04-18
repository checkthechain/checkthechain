from __future__ import annotations

import functools
import typing

from typing_extensions import TypedDict

from ctc.toolbox import search_utils
from ctc import spec
from .. import block_crud


class BlockTimestampSearchCache(TypedDict):
    initializing: dict[int, bool]
    timestamps: dict[int, int]


async def async_get_block_of_timestamp_from_node(
    timestamp: int,
    nary: typing.Optional[int] = None,
    cache: typing.Optional[BlockTimestampSearchCache] = None,
    provider: spec.ProviderSpec = None,
    verbose: bool = True,
) -> int:
    """
    - could make this efficiently parallelizable to multiple timestamps by sharing cache
        - would need to remove the initializing key from the shared cache
    """

    if nary is None:
        nary = 6

    if cache is None:
        cache = {'initializing': {timestamp: True}, 'timestamps': {}}

    async_is_match = functools.partial(
        _async_is_match_block_of_timestamp, timestamp=timestamp, cache=cache
    )
    get_next_probes = functools.partial(
        _get_next_probes_block_of_timestamp,
        timestamp=timestamp,
        cache=cache,
        debug=verbose,
    )

    end_index = await block_crud.async_get_latest_block_number(
        provider=provider
    )

    block = await search_utils.async_nary_search(
        nary=nary,
        start_index=1,
        end_index=end_index,
        async_is_match=async_is_match,
        get_next_probes=get_next_probes,
    )

    if block is None:
        raise Exception('could not find block for timestamp')

    return block


async def _async_is_match_block_of_timestamp(
    block_numbers: list[int],
    timestamp: int,
    cache: BlockTimestampSearchCache,
    provider: spec.ProviderSpec = None,
) -> list[bool]:

    # retrieve values not in cache
    not_in_cache = [
        block_number
        for block_number in block_numbers
        if block_number not in cache['timestamps']
    ]
    gotten = await block_crud.async_get_blocks(not_in_cache, provider=provider)
    for block_number, block in zip(not_in_cache, gotten):
        cache['timestamps'][block_number] = block['timestamp']

    # compute results
    return [
        cache['timestamps'][block_number] >= timestamp
        for block_number in block_numbers
    ]


def _get_next_probes_block_of_timestamp(
    nary: int,
    probe_min: int,
    probe_max: int,
    timestamp: int,
    cache: BlockTimestampSearchCache,
    debug: bool = True,
) -> list[int]:
    import numpy as np

    if cache['initializing'][timestamp]:
        cache['initializing'][timestamp] = False
        return search_utils.get_next_probes_linear(probe_min, probe_max, nary)
    else:

        min_timestamp = cache['timestamps'][probe_min]
        total_time = cache['timestamps'][probe_max] - min_timestamp
        total_blocks = probe_max - probe_min
        mean_block_time = total_time / total_blocks
        target_index = probe_min + (timestamp - min_timestamp) / mean_block_time
        target_index = int(target_index)

        if debug:
            print('mean_block_time:', mean_block_time)
            print('probe_min:', probe_min)
            print('min_timestamp:', min_timestamp)
            print('target_index:', target_index)
            print()

        # if narrowing a range larger than N, probe a window of size X centered on target_index
        if probe_max - probe_min > 1000:
            size = probe_max - probe_min
            probes_array = target_index + size * np.linspace(
                -0.01, 0.01, nary - 1
            )
            probes_array = probes_array.astype(int)
            probes = [
                probe
                for probe in probes_array
                if probe <= probe_max and probe >= probe_min
            ]
            return probes

        # else, probe the indices directly surrounding target_index
        else:

            if target_index == probe_max:
                target_index -= 1
            elif target_index == probe_min:
                target_index += 1

            n_probes = nary - 1
            half = int(n_probes / 2)
            probes = [target_index + i for i in range(-half, n_probes - half)]

            return probes

