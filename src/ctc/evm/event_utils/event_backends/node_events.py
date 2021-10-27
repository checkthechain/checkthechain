import pandas as pd
import toolparallel

from ctc.toolbox import etl_utils
from ctc.toolbox import web3_utils
from ... import block_utils
from ... import contract_abi_utils
from ... import event_abi_utils


def get_events_from_node(
    start_block='latest',
    end_block='latest',
    blocks_per_chunk=2000,
    package_as_dataframe=True,
    verbose=True,
    **kwargs
):
    """see fetch_events() for complete kwarg list"""

    blocks_per_chunk = max(100, blocks_per_chunk)

    # create chunks
    if start_block == 'latest':
        start_block = block_utils.fetch_latest_block_number()
    if end_block == 'latest':
        end_block = block_utils.fetch_latest_block_number()
    if verbose:
        print('getting events from node, block range:', [start_block, end_block])
    if blocks_per_chunk is not None:
        chunks = etl_utils.get_chunks_in_range(
            start_block=start_block,
            end_block=end_block,
            chunk_size=blocks_per_chunk,
            trim_excess=True,
        )
    else:
        chunks = [[start_block, end_block]]

    # fetch entries
    contract_abi = contract_abi_utils.get_contract_abi(
        contract_address=kwargs['contract_address'],
    )
    chunks_entries = _get_chunk_of_events_from_node(
        block_ranges=chunks,
        package_as_dataframe=False,
        contract_abi=contract_abi,
        verbose=verbose,
        **kwargs
    )
    entries = [
        entry for chunk_entries in chunks_entries for entry in chunk_entries
    ]

    # package as dataframe
    if package_as_dataframe:
        entries = _package_exported_events(
            entries,
            contract_address=kwargs.get('contract_address'),
            contract_abi=kwargs.get('contract_abi'),
            event_hash=kwargs.get('event_hash'),
            event_name=kwargs.get('event_name'),
        )

    return entries


@toolparallel.parallelize_input(
    singular_arg='block_range', plural_arg='block_ranges', config={'n_workers': 10},
)
def _get_chunk_of_events_from_node(
    block_range=None,
    start_block=None,
    end_block=None,
    event_name=None,
    event_hash=None,
    contract_address=None,
    contract_abi=None,
    contract_name=None,
    project=None,
    package_as_dataframe=True,
    verbose=None,
):
    if contract_abi is None:
        contract_abi = contract_abi_utils.get_contract_abi(
            contract_address=contract_address
        )

    # create contract
    contract = web3_utils.get_web3_contract(
        contract_address=contract_address,
        contract_abi=contract_abi,
        contract_name=contract_name,
        project=project,
    )

    # create event_filter
    if event_name is None and event_hash is None:
        raise Exception('must specify event_name or event_hash')
    if event_name is None:
        event_name = event_abi_utils.get_event_abi(
            event_hash=event_hash,
            contract_abi=contract_abi,
            contract_address=contract_address,
        )['name']
    if start_block is None and end_block is None:
        start_block, end_block = block_range

    event_filter = contract.events[event_name].createFilter(
        fromBlock=int(start_block),
        toBlock=int(end_block),
    )

    # fetch entries
    entries = event_filter.get_all_entries()

    # package data into dataframe
    if package_as_dataframe:
        entries = _package_exported_events(
            entries,
            contract_abi=contract_abi,
            event_hash=event_hash,
            event_name=event_name,
        )

    return entries


def _package_exported_events(
    entries, contract_address, contract_abi, event_hash, event_name
):

    # TODO: return empty dataframe instead
    if len(entries) == 0:
        return create_empty_event_dataframe(
            contract_address=contract_address,
            contract_abi=contract_abi,
            event_hash=event_hash,
            event_name=event_name,
        )

    formatted_entries = []
    for entry in entries:
        formatted_entry = {
            'block_number': entry['blockNumber'],
            'transaction_index': entry['transactionIndex'],
            'log_index': entry['logIndex'],
            'block_hash': entry['blockHash'].hex(),
            'transaction_hash': entry['transactionHash'].hex(),
            'contract_address': entry['address'],
            'event_name': entry['event'],
        }
        for arg_name, arg_value in entry['args'].items():
            formatted_entry['arg__' + arg_name] = arg_value
        formatted_entries.append(formatted_entry)

    df = pd.DataFrame(formatted_entries)
    df = df.set_index(['block_number', 'transaction_index', 'log_index'])

    return df


def create_empty_event_dataframe(
    *,
    event_abi=None,
    contract_address=None,
    contract_abi=None,
    event_hash=None,
    event_name=None
):

    # standard columns
    columns = [
        'block_number',
        'transaction_index',
        'log_index',
        'block_hash',
        'transaction_hash',
        'contract_address',
        'event_name',
    ]

    # event-specific columns
    if event_abi is None:
        event_abi = event_abi_utils.get_event_abi(
            contract_address=contract_address,
            contract_abi=contract_abi,
            event_hash=event_hash,
            event_name=event_name,
        )
    for item in event_abi['inputs']:
        columns.append('arg__' + item['name'])

    df = pd.DataFrame(columns=columns)
    df = df.set_index(['block_number', 'transaction_index', 'log_index'])

    return df

