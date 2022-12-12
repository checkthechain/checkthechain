"""functions for importing legacy ctc event csv's to db"""

from __future__ import annotations

import os
import typing

from ctc import spec
from .. import abi_utils
from .. import block_utils

if typing.TYPE_CHECKING:

    from typing_extensions import TypedDict

    class DirectoryCSVFiles(TypedDict):
        csv_files: typing.Sequence[LegacyCSVFile]
        total_bytes: int

    class LegacyCSVFile(TypedDict):
        path: str
        contract_address: spec.Address
        event_hash: str
        start_block: int
        end_block: int
        network: spec.NetworkReference
        event_abi: spec.EventABI
        latest_block: int


async def async_import_events_dir_to_db(
    *,
    events_dir: str,
    network: spec.NetworkReference,
    verbose: bool = True,
    skip: int | None = None,
) -> DirectoryCSVFiles:
    """import all legacy csv events in root events dir to database"""

    import toolstr

    latest_block = await block_utils.async_get_latest_block_number()

    total_bytes = 0
    csv_files = []
    for parent_dir, subdirs, filenames in os.walk(events_dir):

        parent_dirname = os.path.basename(parent_dir)
        if not parent_dirname.startswith('event__'):
            continue
        event_hash = parent_dirname[7:]

        grandparent_dir = os.path.dirname(parent_dir)
        grandparent_dirname = os.path.basename(grandparent_dir)
        if not grandparent_dirname.startswith('contract__'):
            continue
        contract_address = grandparent_dirname[10:]

        try:
            event_abi = await abi_utils.async_get_event_abi(
                contract_address=contract_address,
                event_hash=event_hash,
                network=network,
            )
        except (spec.AbiNotFoundException, LookupError):
            print(
                'skipping because could not find ABI for contract: '
                + str(contract_address)
                + '__'
                + event_hash
            )
            continue

        for filename in filenames:
            if filename.endswith('csv') and '__to__' in filename:
                head, tail = filename.split('__to__')
                if not head.isnumeric():
                    continue
                if not tail[:-4].isnumeric():
                    continue
                start_block = int(head)
                end_block = int(tail[:-4])

                filepath = os.path.join(parent_dir, filename)
                file: LegacyCSVFile = {
                    'path': filepath,
                    'contract_address': contract_address,
                    'event_hash': event_hash,
                    'start_block': start_block,
                    'end_block': end_block,
                    'network': network,
                    'event_abi': event_abi,
                    'latest_block': latest_block,
                }
                csv_files.append(file)

                total_bytes += os.path.getsize(filepath)

    if verbose:
        print('events directory:', events_dir)
        print()
        print('importing', len(csv_files), 'event csv files to db')
        print()
        print('total csv files size:', toolstr.format_nbytes(total_bytes))
        print()

    next_milestone = 0
    for i, csv_file in enumerate(csv_files):
        if skip is not None and i < skip:
            continue
        if verbose:
            fraction_done = i / len(csv_files)
            if fraction_done >= next_milestone:
                print(
                    'importing',
                    i,
                    '/',
                    len(csv_files),
                    'contract=' + csv_file['contract_address'],
                    'event=' + csv_file['event_hash'][:12] + '...',
                )
        await async_import_events_csv_file_to_db(**csv_file)

    if verbose:
        print()
        print('import of directory complete')

    return {
        'csv_files': csv_files,
        'total_bytes': total_bytes,
    }


async def async_import_events_csv_file_to_db(
    *,
    path: str,
    contract_address: spec.Address,
    event_hash: str,
    start_block: int,
    end_block: int,
    network: spec.NetworkReference,
    event_abi: spec.EventABI,
    latest_block: int | None = None,
) -> None:

    import ast
    import pandas as pd
    from ctc import db

    # load data
    events = pd.read_csv(path)

    # modify columns
    events['event_hash'] = event_hash
    if 'address' in events.columns:
        del events['address']
    del events['block_hash']

    # check columns present
    required_columns = [
        'block_number',
        'transaction_index',
        'log_index',
        'event_hash',
        'transaction_hash',
        'contract_address',
        'event_name',
    ]
    for column in required_columns:
        if column not in events:
            raise Exception('column missing from file: ' + str(column))
    for column in events.columns.values.tolist():
        if column not in required_columns and not column.startswith('arg__'):
            raise Exception('extra column in file: ' + str(column))

    # convert complex types from str to native types
    indexed_names = abi_utils.get_event_indexed_names(event_abi)
    indexed_types = abi_utils.get_event_indexed_types(event_abi)
    unindexed_names = abi_utils.get_event_unindexed_names(event_abi)
    unindexed_types = abi_utils.get_event_unindexed_types(event_abi)
    names = indexed_names + unindexed_names
    types = indexed_types + unindexed_types
    for name, arg_type in zip(names, types):
        if arg_type.endswith(']') or arg_type in ['bytes', 'bytes32']:
            column = 'arg__' + name
            events[column] = events[column].map(lambda x: ast.literal_eval(x))
        elif arg_type.startswith('int') or arg_type.startswith('uint'):
            column = 'arg__' + name
            events[column] = events[column].map(int)

    # set index
    events = events.set_index(
        ['block_number', 'transaction_index', 'log_index']
    )

    # encode fields
    encoded_events = abi_utils.encode_events_dataframe_event_type(
        events=events,
        event_abi=event_abi,
    )

    # convert nan's to None
    for column in encoded_events.columns:
        mask = encoded_events[column].isnull()
        if mask.any():
            encoded_events[column] = encoded_events[column].astype(object)
            encoded_events[column].values[mask] = None  # type: ignore

    # construct query
    event_query: spec.DBEventQuery = {
        'query_type': 1,
        'contract_address': contract_address,
        'event_hash': event_hash,
        'start_block': start_block,
        'end_block': end_block,
        'topic1': None,
        'topic2': None,
        'topic3': None,
    }

    # insert into database
    if latest_block is None:
        latest_block = await block_utils.async_get_latest_block_number()
    await db.async_intake_encoded_events(
        encoded_events=encoded_events,
        query=event_query,
        network=network,
        latest_block=latest_block,
    )

    # validate result
    pass
