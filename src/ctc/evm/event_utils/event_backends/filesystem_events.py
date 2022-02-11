"""need to refactor with common backend interface"""

from __future__ import annotations

import ast
import functools
import os
import typing
from typing_extensions import TypedDict

import toolstr

import ctc.config
from ctc import binary
from ctc import directory
from ctc import spec
from ctc import rpc
from ctc.toolbox import backend_utils
from ctc.toolbox import filesystem_utils
from ... import abi_utils
from ... import block_utils
from ... import evm_spec


#
# # paths
#


def get_events_root(
    network: typing.Optional[spec.NetworkReference] = None,
) -> str:
    network_name = directory.get_network_name(network)
    return os.path.join(ctc.config.get_data_dir(), network_name, 'events')


def get_events_contract_dir(
    contract_address: spec.Address,
    network: typing.Optional[spec.NetworkReference] = None,
) -> str:
    contract_address = contract_address.lower()
    return os.path.join(
        get_events_root(network=network), 'contract__' + contract_address
    )


def get_events_event_dir(
    contract_address: spec.Address,
    event_hash: typing.Optional[str] = None,
    event_abi: typing.Optional[spec.EventABI] = None,
    network: typing.Optional[spec.NetworkReference] = None,
) -> str:
    contract_address = contract_address.lower()
    if event_hash is None:
        if event_abi is None:
            raise Exception('must specify more event data')
        event_hash = binary.get_event_hash(event_abi)
    contract_dir = get_events_contract_dir(contract_address, network=network)
    return os.path.join(contract_dir, 'event__' + event_hash)


def get_events_filepath(
    contract_address: spec.Address,
    start_block: int,
    end_block: int,
    event_hash: typing.Optional[str] = None,
    event_abi: typing.Optional[spec.EventABI] = None,
    network: typing.Optional[spec.NetworkReference] = None,
) -> str:

    # create lowercase versions of contract_address and event_hash
    contract_address = contract_address.lower()
    if event_hash is None:
        if event_abi is None:
            raise Exception('must specify more event data')
        event_hash = binary.get_event_hash(event_abi)
    event_hash = event_hash.lower()

    # assemble items into subpath
    subpath = evm_spec.filesystem_layout['evm_events_path'].format(
        contract_address=contract_address,
        event_hash=event_hash,
        start_block=start_block,
        end_block=end_block,
    )

    # add parent directory
    network_name = directory.get_network_name(network)
    return os.path.join(ctc.config.get_data_dir(), network_name, subpath)


#
# # list saved data
#


def list_events_contracts(
    network: typing.Optional[spec.NetworkReference] = None,
) -> list[str]:
    contracts = []
    events_root = get_events_root(network=network)
    if not os.path.isdir(events_root):
        return []
    for contract_dir in os.listdir(events_root):
        contract_address = contract_dir.split('__')[-1]
        contracts.append(contract_address)
    return contracts


_PathEventsResult = typing.Dict[str, typing.Tuple[int, int]]


class _ListEventsResult(TypedDict):
    paths: _PathEventsResult
    block_range: spec.NumpyArray
    block_mask: spec.NumpyArray
    missing_blocks: spec.NumpyArray


def list_contract_events(
    contract_address: spec.Address,
    event_hash: typing.Optional[str] = None,
    event_abi: typing.Optional[spec.EventABI] = None,
    allow_missing_blocks: bool = False,
    network: typing.Optional[spec.NetworkReference] = None,
) -> dict[str, _ListEventsResult]:

    if event_hash is not None:
        query_event_hash = event_hash
    elif event_abi is not None:
        query_event_hash = binary.get_event_hash(event_abi)
    else:
        query_event_hash = None

    # compile path data
    contract_address = contract_address.lower()
    contract_dir = get_events_contract_dir(contract_address, network=network)
    paths: dict[str, _PathEventsResult] = {}
    if not os.path.isdir(contract_dir):
        return {}
    for event_dirname in os.listdir(contract_dir):
        event_dir = os.path.join(contract_dir, event_dirname)
        _, event_hash = event_dirname.split('__')
        if query_event_hash is not None and event_hash != query_event_hash:
            continue
        for filename in os.listdir(event_dir):
            path = os.path.join(event_dir, filename)
            start_block_str, _, end_block_str = os.path.splitext(filename)[
                0
            ].split('__')
            paths.setdefault(event_hash, {})
            paths[event_hash][path] = (int(start_block_str), int(end_block_str))

    import numpy as np

    # create block_range and block_mask
    events: dict[str, _ListEventsResult] = {}
    for event_hash in paths.keys():

        # gather start and end blocks
        start_blocks = []
        end_blocks = []
        for path, (start_block, end_block) in paths[event_hash].items():
            start_blocks.append(start_block)
            end_blocks.append(end_block)

        # create block_range
        min_block = min(start_blocks)
        max_block = max(end_blocks) + 1
        block_range = np.arange(min_block, max_block)

        # create block_mask
        n_blocks = block_range.size
        block_mask = np.zeros(n_blocks)
        for path, (start_block, end_block) in paths[event_hash].items():
            start_index = start_block - min_block
            end_index = n_blocks - (max_block - end_block) + 1
            block_mask[start_index:end_index] += 1
        if (block_mask > 1).sum() > 0:
            raise Exception('overlapping chunks')
        block_mask = block_mask.astype(bool)

        # check if blocks missing
        missing_blocks = block_mask.sum() != n_blocks
        if missing_blocks and not allow_missing_blocks:
            raise Exception('missing blocks')

        events[event_hash] = {
            'paths': paths[event_hash],
            'block_range': block_range,
            'block_mask': block_mask,
            'missing_blocks': missing_blocks,
        }

    return events


def list_events(
    contract_address: str,
    event_hash: typing.Optional[str] = None,
    event_abi: typing.Optional[spec.EventABI] = None,
    allow_missing_blocks: bool = False,
    network: typing.Optional[spec.NetworkReference] = None,
) -> typing.Optional[_ListEventsResult]:

    contract_events = list_contract_events(
        contract_address=contract_address,
        event_hash=event_hash,
        event_abi=event_abi,
        allow_missing_blocks=allow_missing_blocks,
        network=network,
    )

    if len(contract_events) == 1:
        event_hash = list(contract_events.keys())[0]
        return contract_events[event_hash]
    else:
        return None


def list_contracts_events(
    network: typing.Optional[spec.NetworkReference] = None, **kwargs
) -> dict[str, dict[str, _ListEventsResult]]:
    contracts_events = {}
    for contract_address in list_events_contracts(network=network):
        contracts_events[contract_address] = list_contract_events(
            contract_address=contract_address, network=network, **kwargs
        )
    return contracts_events


#
# # disk
#


def print_events_summary() -> None:
    print_events_summary_filesystem()


def print_events_summary_filesystem() -> None:
    contracts_events = list_contracts_events()
    print('## Contracts (' + str(len(contracts_events)) + ')')
    for contract_address in sorted(contracts_events.keys()):
        n_events = len(contracts_events[contract_address])
        print('-', contract_address, '(' + str(n_events) + ' events)')
        contract_events = contracts_events[contract_address]
        for event_hash, event_data in contract_events.items():
            block_range = [
                event_data['block_range'][0],
                event_data['block_range'][-1],
            ]
            n_files = str(len(event_data['paths']))
            dirpath = get_events_event_dir(
                contract_address=contract_address, event_hash=event_hash
            )
            n_bytes = filesystem_utils.get_directory_nbytes_human(dirpath)
            short_hash = event_hash[:6] + '...' + event_hash[-6:]
            print(
                '    -',
                short_hash,
                block_range,
                '(' + n_bytes + 'B in ' + n_files + ' files)',
            )


async def async_save_events_to_filesystem(
    events: spec.DataFrame,
    contract_address: spec.Address,
    start_block: int,
    end_block: int,
    event_abi: typing.Optional[spec.EventABI] = None,
    event_hash: typing.Optional[str] = None,
    event_name: typing.Optional[str] = None,
    overwrite: bool = False,
    verbose: bool = True,
    provider: spec.ProviderSpec = None,
    network: typing.Optional[spec.NetworkReference] = None,
) -> str:

    if network is None:
        provider = rpc.get_provider(provider)
        network = provider['network']
        if network is None:
            raise Exception('could not determine network')
    else:
        network = directory.get_network_name(network)

    contract_address = contract_address.lower()

    if event_abi is None:
        event_abi = await abi_utils.async_get_event_abi(
            contract_address=contract_address,
            event_name=event_name,
            event_hash=event_hash,
            network=network,
        )

    # compute path
    path = get_events_filepath(
        contract_address=contract_address,
        event_hash=event_hash,
        event_abi=event_abi,
        start_block=start_block,
        end_block=end_block,
        network=network,
    )
    if os.path.exists(path) and not overwrite:
        raise Exception('path already exists, use overwrite=True')

    if verbose:
        print('saving events to file:', path)

    # save
    os.makedirs(os.path.dirname(path), exist_ok=True)
    events.to_csv(path)

    return path


async def async_get_events_from_filesystem(
    contract_address: spec.ContractAddress,
    event_hash: typing.Optional[str] = None,
    event_name: typing.Optional[str] = None,
    event_abi: typing.Optional[spec.EventABI] = None,
    verbose: bool = True,
    start_block: typing.Optional[int] = None,
    end_block: typing.Optional[int] = None,
    provider: spec.ProviderSpec = None,
    network: spec.NetworkReference = None,
) -> spec.DataFrame:

    # get network
    if network is None:
        provider = rpc.get_provider(provider)
        network = provider['network']
        if network is None:
            raise Exception('could not determine network')
    else:
        network = directory.get_network_name(network)

    # resolve start_block and end_block
    if start_block is not None:
        start_block = await block_utils.async_block_number_to_int(
            start_block,
            provider=provider,
        )
    if end_block is not None:
        end_block = await block_utils.async_block_number_to_int(
            end_block,
            provider=provider,
        )

    # get event hash
    if event_hash is None:
        if event_abi is None:
            if event_name is None:
                raise Exception('must specify more event information')
            event_abi = await abi_utils.async_get_event_abi(
                contract_address=contract_address,
                event_name=event_name,
                network=network,
            )

        event_hash = binary.get_event_hash(event_abi)

    events = list_contract_events(
        contract_address=contract_address,
        event_abi=event_abi,
        event_hash=event_hash,
        network=network,
    )
    if event_hash not in events or len(events[event_hash]['paths']) == 0:
        raise backend_utils.DataNotFound('no files for event')

    # get paths to load
    paths_to_load = []
    for path, (path_start, path_end) in events[event_hash]['paths'].items():
        if start_block is not None:
            if path_end < start_block:
                continue
        if end_block is not None:
            if end_block < path_start:
                continue
        paths_to_load.append(path)
    if len(paths_to_load) == 0:
        raise backend_utils.DataNotFound('no files for event')

    # print summary
    if verbose:
        if len(paths_to_load) > 0:
            n_files = len(paths_to_load)
            n_bytes_int = sum(os.path.getsize(path) for path in paths_to_load)
            n_bytes = toolstr.format(n_bytes_int / 1024 / 1024) + 'M'
        else:
            n_bytes = '0'
            n_files = 0
        print('loading events (' + n_bytes + 'B', 'across', n_files, 'files)')
        if verbose >= 2:
            for path in paths_to_load:
                print('-', path)

    import pandas as pd

    # load paths
    dfs = []
    for path in paths_to_load:
        df = pd.read_csv(path)
        df = df.set_index(['block_number', 'transaction_index', 'log_index'])
        dfs.append(df)
    df = pd.concat(dfs, axis=0)
    df = df.sort_index()

    # trim unwanted
    if start_block is not None:
        if start_block < events[event_hash]['block_range'][0]:
            raise backend_utils.DataNotFound(
                'start_block outside of filesystem contents'
            )
        mask = df.index.get_level_values(level='block_number') >= start_block
        df = df[mask]
    if end_block is not None:
        if end_block > events[event_hash]['block_range'][-1]:
            raise backend_utils.DataNotFound(
                'end_block outside of filesystem contents'
            )
        mask = df.index.get_level_values(level='block_number') <= end_block
        df = df[mask]

    # convert any bytes
    prefix = 'arg__'
    if event_abi is None:
        event_abi = await abi_utils.async_get_event_abi(
            contract_address=contract_address,
            event_name=event_name,
            event_hash=event_hash,
            network=network,
        )
    for arg in event_abi['inputs']:
        if arg['type'] in ['bytes32']:
            column = prefix + arg['name']
            lam = functools.partial(
                binary.convert,
                output_format='prefix_hex',
            )
            df[column] = df[column].map(ast.literal_eval).map(lam)

    return df

