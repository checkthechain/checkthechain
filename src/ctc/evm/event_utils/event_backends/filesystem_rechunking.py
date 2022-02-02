import math
import os
import typing

import toolstr

from ctc import evm
from ctc import binary
from ctc import spec

from . import filesystem_events
from ... import abi_utils


async def async_rechunk_events(
    contract_address: spec.Address,
    chunk_target_bytes: int,
    event_name: typing.Optional[str] = None,
    event_hash: typing.Optional[str] = None,
    start_block: typing.Optional[spec.BlockNumberReference] = None,
    end_block: typing.Optional[spec.BlockNumberReference] = None,
    chunk_size_tolerance: float = 0.1,
    verbose: bool = True,
    dry: bool = False,
    network: spec.NetworkReference = 'mainnet',
):
    import numpy as np

    # get event hash
    if event_hash is None:
        if event_name is None:
            raise Exception('must specify event_name or event_name')
        event_abi = await abi_utils.async_get_event_abi(
            contract_address=contract_address, event_name=event_name
        )
        event_name = binary.get_event_hash(event_abi)

    # make sure no leftover files from previous rechunks
    event_list = filesystem_events.list_events(
        contract_address=contract_address,
        event_hash=event_hash,
        network=network,
    )
    if event_list is None:
        if verbose:
            print('skipping rechunk, no event data found')
        return
    for path in event_list['paths']:
        if path.endswith('__OLD'):
            event_dir = filesystem_events.get_events_event_dir(
                contract_address=contract_address,
                event_hash=event_hash,
                network=network,
            )
            message = (
                'there exists <filename>__OLD files from an incomplete'
                ' rechunking, remove these files to continue in directory '
            ) + str(event_dir)
            raise Exception(message)

    # load events
    if start_block is not None:
        start_block = await evm.async_block_number_to_int(start_block)
    if end_block is not None:
        end_block = await evm.async_block_number_to_int(end_block)

    # get event range
    if start_block is None:
        start_block = min(
            path_start for path_start, path_end in event_list['paths'].values()
        )
    if end_block is None:
        end_block = max(
            path_end for path_start, path_end in event_list['paths'].values()
        )
    start_block = typing.cast(int, start_block)
    end_block = typing.cast(int, end_block)

    # get original files of block range
    original_paths = []
    for path, (path_start, path_end) in event_list['paths'].items():
        if (start_block <= path_start and path_start <= end_block) or (
            start_block <= end_block and end_block <= end_block
        ):
            original_paths.append(path)
    original_paths = sorted(original_paths)

    # eliminate paths that are within chunk size tolerance
    path_sizes = {}
    min_path_size = chunk_target_bytes * (1 - chunk_size_tolerance)
    max_path_size = chunk_target_bytes * (1 + chunk_size_tolerance)
    n_trim_start = 0
    for original_path in original_paths:
        path_bytes = os.path.getsize(original_path)
        path_sizes[original_path] = path_bytes
        if min_path_size <= path_bytes and path_bytes <= max_path_size:
            n_trim_start += 1
        else:
            break
    original_paths = original_paths[n_trim_start:]
    n_trim_end = 0
    for original_path in original_paths[::-1]:
        if original_path not in path_sizes:
            path_bytes = os.path.getsize(original_path)
            path_sizes[original_path] = path_bytes
        if min_path_size <= path_bytes and path_bytes <= max_path_size:
            n_trim_end += 1
        else:
            break
    if n_trim_end > 0:
        original_paths = original_paths[:-n_trim_end]

    if len(original_paths) == 1 and path_sizes[original_path] < max_path_size:
        original_paths = []

    # get block range of target paths
    min_block_start = int(float(1e99))
    max_block_end = -1
    for path in original_paths:
        path_start, path_end = event_list['paths'][path]
        min_block_start = min(path_start, min_block_start)
        max_block_end = max(path_end, max_block_end)

    # compute total bytes across all files
    data_bytes = 0
    for original_path in original_paths:
        if original_path not in path_sizes:
            path_sizes[original_path] = os.path.getsize(original_path)
        data_bytes += path_sizes[original_path]

    # compute number of chunks
    n_chunks = math.ceil(data_bytes / chunk_target_bytes)

    # load events
    if len(original_paths) > 0:
        events = await filesystem_events.async_get_events_from_filesystem(
            contract_address=contract_address,
            event_hash=event_hash,
            start_block=min_block_start,
            end_block=max_block_end,
            network=network,
        )

    # split into chunks
    if len(original_paths) > 0 and len(events) > 0:
        event_chunks = typing.cast(
            typing.Sequence[spec.DataFrame],
            np.array_split(events, n_chunks),
        )
    else:
        event_chunks = []

    # get each chunk's block range
    chunk_ranges = []
    for event_chunk in event_chunks:
        chunk_start_block = event_chunk.index.values[0][0]
        chunk_end_block = event_chunk.index.values[-1][0]
        chunk_ranges.append([chunk_start_block, chunk_end_block])

    # remove gaps between block ranges
    for e, (start_block, end_block) in enumerate(chunk_ranges):
        if e + 1 < len(chunk_ranges):
            chunk_ranges[e][1] = chunk_ranges[e + 1][0] - 1

    # remove gaps at beginning and end of ranges
    if len(chunk_ranges) > 0:
        chunk_ranges[0][0] = min(min_block_start, chunk_ranges[0][0])
        chunk_ranges[-1][1] = max(max_block_end, chunk_ranges[-1][1])

    # print summary
    if verbose or dry:
        event_dir = filesystem_events.get_events_event_dir(
            contract_address=contract_address,
            event_hash=event_hash,
            network=network,
        )
        if dry:
            print('[DRY RUN -- WILL NOT CHANGE FILES]')
        print('event rechunking')
        print('- contract:', contract_address)
        print('- event_hash:', event_hash)
        print('- block range', [start_block, end_block])
        print('- data_bytes:', toolstr.format(data_bytes))
        print('- directory:', event_dir)
        print()
        if len(chunk_ranges) == 0:
            print('current chunks acceptable, no rechunking required')
        else:
            print(
                'rechunking',
                len(original_paths),
                'files into',
                n_chunks,
                'files',
            )

    if dry:
        print('[DRY RUN -- NO FILES MODIFIED]')
        return

    if len(chunk_ranges) == 0:
        return

    # rename original files
    for original_path in original_paths:
        os.rename(original_path, original_path + '__OLD')

    # save chunks
    for event_chunk, chunk_range in zip(event_chunks, chunk_ranges):
        chunk_start_block, chunk_end_block = chunk_range
        path = await filesystem_events.async_save_events_to_filesystem(
            events=event_chunk,
            contract_address=contract_address,
            event_hash=event_hash,
            start_block=chunk_start_block,
            end_block=chunk_end_block,
            network=network,
        )

    # remove original files
    for original_path in original_paths:
        os.remove(original_path + '__OLD')

    if verbose:
        print()
        print('...done')


async def async_rechunk_all_events(
    chunk_target_bytes: int,
    network: spec.NetworkReference = 'mainnet',
    start_block: typing.Optional[spec.BlockNumberReference] = None,
    end_block: typing.Optional[spec.BlockNumberReference] = None,
    chunk_size_tolerance: float = 0.1,
    verbose: bool = True,
    dry: bool = False,
):
    contracts_events = filesystem_events.list_contracts_events(network=network)

    for contract_address, events_data in contracts_events.items():
        for event_hash, event_data in events_data.items():
            await async_rechunk_events(
                contract_address=contract_address,
                event_hash=event_hash,
                start_block=start_block,
                end_block=end_block,
                chunk_target_bytes=chunk_target_bytes,
                chunk_size_tolerance=chunk_size_tolerance,
                verbose=verbose,
                dry=dry,
            )
            if verbose:
                print()
                print()

