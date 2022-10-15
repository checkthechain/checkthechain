from __future__ import annotations

import os
import typing

from ctc import spec

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


def import_events_directory_to_db(
    *, path: str, network: spec.NetworkReference, verbose: bool = True,
) -> DirectoryCSVFiles:

    import toolstr

    total_bytes = 0
    csv_files = []
    for parent_dir, subdirs, filenames in os.walk(path):

        if not parent_dir.startswith('event__'):
            continue
        event_hash = parent_dir[7:]

        grandparent_dir = os.path.dirname(parent_dir)
        if not grandparent_dir.startswith('contract__'):
            continue
        contract_address = grandparent_dir[10:]

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
                }
                csv_files.append(file)

                total_bytes += os.path.getsize(filepath)

    if verbose:
        print('root directory:', path)
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
) -> None:

    import pandas as pd

    events = pd.read_csv(path)
    required_columns = [
        'block_number',
        'transaction_index',
        'log_index',
        'address',
        'block_hash',
        'transaction_hash',
        'contract_address',
        'event_name',
        'event_hash',
    ]
    for column in required_columns:
        assert column in events

    raise NotImplementedError('need to re-code topics and unindexed data')
