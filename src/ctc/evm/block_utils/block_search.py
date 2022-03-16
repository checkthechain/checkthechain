from __future__ import annotations

import asyncio
import functools
import typing
from typing_extensions import TypedDict

import tooltime

from ctc import spec
from ctc.toolbox import search_utils
from .. import address_utils
from . import block_crud


class BlockTimestampSearchCache(TypedDict):
    initializing: dict[int, bool]
    timestamps: dict[int, int]


async def async_get_contract_creation_block(
    contract_address: spec.Address,
    start_block: typing.Optional[spec.BlockNumberReference] = None,
    end_block: typing.Optional[spec.BlockNumberReference] = None,
    provider: spec.ProviderSpec = None,
    verbose: bool = True,
    nary: typing.Optional[int] = None,
) -> int:
    """get the block where a contract was created

    algorithm: perform a binary search across blocks, check code bytes in each
    """

    contract_address = address_utils.get_address_checksum(contract_address)

    if start_block is None:
        start_block = 0
    if end_block is None:
        end_block = 'latest'
    if start_block == 'latest' or end_block == 'latest':
        latest_block = await block_crud.async_get_latest_block_number(
            provider=provider
        )
        if start_block == 'latest':
            start_block = latest_block
        if end_block == 'latest':
            end_block = latest_block

    if verbose:
        print('searching for creation block of ' + contract_address)

    async def async_is_match(index):
        if verbose:
            print('- trying block:', index)
        return await address_utils.async_is_contract_address(
            address=contract_address,
            block=index,
            provider=provider,
        )

    if nary is None:
        result = await search_utils.async_binary_search(
            start_index=start_block,
            end_index=end_block,
            async_is_match=async_is_match,
        )
    else:
        raise NotImplementedError()

    if verbose:
        print('result:', result)

    return result


async def async_get_blocks_of_timestamps(
    timestamps: typing.Sequence[int],
    block_timestamps: typing.Optional[typing.Mapping[int, int]] = None,
    block_number_array: typing.Optional[spec.NumpyArray] = None,
    block_timestamp_array: typing.Optional[spec.NumpyArray] = None,
    nary: typing.Optional[int] = None,
    cache: typing.Optional[BlockTimestampSearchCache] = None,
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
            block = get_block_of_timestamp_from_arrays(
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
            coroutine = async_get_block_of_timestamp(
                timestamp=timestamp,
                verbose=False,
                cache=cache,
                nary=nary,
                provider=provider,
            )
            coroutines.append(coroutine)

        return await asyncio.gather(*coroutines)


async def async_get_block_of_timestamp(
    timestamp: tooltime.Timestamp,
    nary: typing.Optional[int] = None,
    cache: typing.Optional[BlockTimestampSearchCache] = None,
    block_timestamps: typing.Optional[typing.Mapping[int, int]] = None,
    block_timestamp_array: typing.Optional[spec.NumpyArray] = None,
    block_number_array: typing.Optional[spec.NumpyArray] = None,
    verbose: bool = True,
    provider: spec.ProviderSpec = None,
) -> int:
    import numpy as np

    if not isinstance(timestamp, int):
        timestamp = tooltime.timestamp_to_seconds(timestamp)

    if block_timestamps is not None or (
        block_timestamp_array is not None and block_number_array is not None
    ):
        if block_timestamp_array is None:
            if block_timestamps is None:
                raise Exception('must specify more arguments')
            block_timestamp_array = np.array(list(block_timestamps.values()))
        if block_number_array is None:
            if block_timestamps is None:
                raise Exception('must specify more arguments')
            block_number_array = np.array(list(block_timestamps.keys()))

        return get_block_of_timestamp_from_arrays(
            timestamp=timestamp,
            block_timestamp_array=block_timestamp_array,
            block_number_array=block_number_array,
            verbose=verbose,
        )
    else:
        return await async_get_block_of_timestamp_from_node(
            timestamp=timestamp,
            nary=nary,
            cache=cache,
            verbose=verbose,
            provider=provider,
        )


def get_block_of_timestamp_from_arrays(
    timestamp: tooltime.Timestamp,
    block_timestamp_array: spec.NumpyArray,
    block_number_array: spec.NumpyArray,
    verbose: bool,
) -> int:
    import numpy as np

    if not isinstance(timestamp, int):
        timestamp = tooltime.timestamp_to_seconds(timestamp)

    index = np.searchsorted(block_timestamp_array, timestamp)
    return block_number_array[index]


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

    return await search_utils.async_nary_search(
        nary=nary,
        start_index=1,
        end_index=end_index,
        async_is_match=async_is_match,
        get_next_probes=get_next_probes,
    )


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


async def async_get_block_number_and_time(
    block_number: typing.Optional[spec.BlockNumberReference] = None,
    block_timestamp: typing.Optional[tooltime.Timestamp] = None,
    provider: spec.ProviderSpec = None,
) -> tuple[int, int]:

    if block_timestamp is not None and block_number is not None:
        raise Exception('must specify start_time or block_number')

    if block_number is not None:
        block = await block_crud.async_get_block(
            block_number, provider=provider
        )
        return block['number'], block['timestamp']

    elif block_timestamp is not None:
        block_number = await async_get_block_of_timestamp(
            block_timestamp, provider=provider
        )
        block = await block_crud.async_get_block(
            block_number, provider=provider
        )
        return block['number'], block['timestamp']

    else:
        raise Exception('must specify start_time or block_number')

