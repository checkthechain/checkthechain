# TODO: rename this file to block_time_rpc
from __future__ import annotations

import functools
import typing

from ctc import spec
from .. import block_crud

if typing.TYPE_CHECKING:
    from typing_extensions import TypedDict, Literal

    class BlockTimestampSearchCache(TypedDict):
        initializing: dict[int, bool]
        timestamps: dict[int, int]


async def _async_get_block_of_timestamp_from_node(
    timestamp: int,
    *,
    nary: typing.Optional[int] = None,
    cache: typing.Optional[BlockTimestampSearchCache] = None,
    provider: spec.ProviderReference = None,
    mode: Literal['<=', '>=', '=='] = '>=',
    verbose: bool = True,
    use_db_assist: bool = True,
) -> int:
    """

    - could make this efficiently parallelizable to multiple timestamps by sharing cache
        - would need to remove the initializing key from the shared cache
    """

    from ctc.toolbox import search_utils

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

    # determine search range
    start_index: int | None = None
    end_index: int | None = None
    if use_db_assist:
        from ctc import db
        from ctc import rpc

        network = rpc.get_provider_network(provider)
        result = await db.async_query_timestamp_block_range(
            timestamp, network=network
        )
        if result is not None:
            start_index, end_index = result
            if start_index == end_index and start_index is not None:
                return start_index
    if start_index is None:
        start_index = 1
    if end_index is None:
        end_index = await block_crud.async_get_latest_block_number(
            provider=provider
        )

    try:
        block = await search_utils.async_nary_search(
            nary=nary,
            start_index=start_index,
            end_index=end_index,
            async_is_match=async_is_match,
            get_next_probes=get_next_probes,
        )
    except search_utils.SearchRangeTooLow:
        if mode == '<=':
            return end_index
        else:
            raise Exception('no block after timestamp: ' + str(timestamp))

    if block is None:
        raise Exception('could not find block for timestamp')

    if mode == '==':
        block_data = await block_crud.async_get_block(block)
        if block_data['timestamp'] == timestamp:
            return block
        else:
            raise Exception(
                'there is no block with timestamp ' + str(timestamp)
            )
    elif mode == '<=':
        if block == 0:
            raise Exception('no block exists <= timestamp')
        block_data = await block_crud.async_get_block(block)
        if block_data['timestamp'] == timestamp:
            return block
        else:
            return block - 1
    else:
        return block


async def _async_is_match_block_of_timestamp(
    block_numbers: list[int],
    timestamp: int,
    *,
    cache: BlockTimestampSearchCache,
    provider: spec.ProviderReference = None,
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
    *,
    nary: int,
    probe_min: int,
    probe_max: int,
    timestamp: int,
    cache: BlockTimestampSearchCache,
    debug: bool = True,
) -> list[int]:

    import numpy as np
    from ctc.toolbox import search_utils

    if cache['initializing'][timestamp]:
        cache['initializing'][timestamp] = False
        return search_utils.get_next_probes_linear(
            probe_min=probe_min, probe_max=probe_max, nary=nary
        )
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
