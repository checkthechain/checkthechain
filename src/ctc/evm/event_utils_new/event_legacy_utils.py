"""functions for importing legacy ctc event csv's to db"""

from __future__ import annotations

import os
import typing

from ctc import spec
from .. import abi_utils

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


async def async_import_events_dir_to_db(
    *, events_dir: str, network: spec.NetworkReference, verbose: bool = True,
) -> DirectoryCSVFiles:

    import toolstr

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
            print('skipping because could not find ABI for contract: ' + str(contract_address))
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
        if verbose:
            fraction_done = i / len(csv_files)
            if fraction_done >= next_milestone:
                print(i, '/', len(csv_files), 'complete')
        import_events_csv_file_to_db(**csv_file)

    if verbose:
        print()
        print('import of directory complete')

    return {
        'csv_files': csv_files,
        'total_bytes': total_bytes,
    }


def import_events_csv_file_to_db(
    *,
    path: str,
    contract_address: spec.Address,
    event_hash: str,
    start_block: int,
    end_block: int,
    network: spec.NetworkReference,
    event_abi: spec.EventABI,
) -> None:

    import pandas as pd

    events = pd.read_csv(path)

    # check columns present
    required_columns = [
        'block_number',
        'transaction_index',
        'log_index',
        'block_hash',
        'transaction_hash',
        'contract_address',
        'event_name',
    ]
    for column in required_columns:
        if column not in events:
            raise Exception('column missing from file: ' + str(column))
    for column in events.columns.values.tolist():
        if column not in required_columns and not column.startswith('arg__'):
            raise Exception()

    event_query = {
        'query_type': 1,
        'contract_address': contract_address,
        'event_hash': event_hash,
        'start_block': start_block,
        'end_block': end_block,
    }

    # encode the topics
    pass

    raise NotImplementedError('need to re-code topics and unindexed data')
