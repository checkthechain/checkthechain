import functools

from ctc.toolbox import search_utils
from .. import address_utils
from .. import rpc_utils
from . import block_crud


def get_contract_creation_block(
    contract_address,
    start_block=None,
    end_block=None,
    provider=None,
    verbose=True,
    nary=None,
):
    """get the block where a contract was created

    algorithm: perform a binary search across blocks, check code bytes in each
    """

    contract_address = address_utils.get_address_checksum(contract_address)

    if start_block is None:
        start_block = 0
    if end_block is None:
        end_block = 'latest'
    if start_block == 'latest' or end_block == 'latest':
        latest_block = block_crud.get_block_number('latest')
        if start_block == 'latest':
            start_block = latest_block
        if end_block == 'latest':
            end_block = latest_block

    def is_match(index):
        if verbose:
            print('trying block:', index)
        code = rpc_utils.eth_get_code(
            address=contract_address, block_number=index, provider=provider
        )
        return len(code) > 3

    if nary is None:
        result = search_utils.binary_search(
            start_index=start_block,
            end_index=end_block,
            is_match=is_match,
        )
    else:
        result = search_utils.nary_search(
            start_index=start_block,
            end_index=end_block,
            is_match=is_match,
            nary=nary,
        )

    if verbose:
        print('result:', result)

    return result


def get_block_of_timestamp(timestamp, nary=None, cache=None):
    """
    - could make this efficiently parallelizable to multiple timestamps by sharing cache
        - would need to remove the initializing key from the shared cache
    """

    if nary is None:
        nary = 6

    if cache is None:
        cache = {'initializing': {timestamp: True}, 'timestamps': {}}

    return search_utils.nary_search(
        nary=nary,
        start_index=1,
        end_index=int(13e6),
        is_match=functools.partial(
            _is_match_block_of_timestamp, timestamp=timestamp, cache=cache
        ),
        get_next_probes=functools.partial(
            _get_next_probes_block_of_timestamp,
            timestamp=timestamp,
            cache=cache,
        ),
    )


def _is_match_block_of_timestamp(block_numbers, timestamp, cache):

    # retrieve values not in cache
    not_in_cache = [
        block_number
        for block_number in block_numbers
        if block_number not in cache['timestamps']
    ]
    gotten = block_crud.get_blocks(not_in_cache)
    for block_number, block in zip(not_in_cache, gotten):
        cache['timestamps'][block_number] = block['timestamp']

    # compute results
    return [
        cache['timestamps'][block_number] >= timestamp
        for block_number in block_numbers
    ]


def _get_next_probes_block_of_timestamp(
    nary, probe_min, probe_max, timestamp, cache, debug=True
):
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
            probes = target_index + size * np.linspace(-0.01, 0.01, nary - 1)
            probes = probes.astype(int)
            probes = [
                probe
                for probe in probes
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


#
# # async versions
#


async def get_blocks_of_timestamps(timestamps, nary=None):
    if cache is None:
        cache = {
            'initializing': {timestamp: True for timestamp in timestamps},
            'timestamps': {},
        }

    # for timestamp in timestamps:
    #     asyncio.create_task(async_get_block_of_timestamp)

