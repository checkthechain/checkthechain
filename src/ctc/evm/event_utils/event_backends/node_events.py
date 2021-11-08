import toolparallel

from ... import block_utils
from ... import contract_abi_utils
from ... import rpc_utils


def get_events_from_node(
    start_block='latest',
    end_block='latest',
    event_name=None,
    event_hash=None,
    contract_address=None,
    contract_abi=None,
    blocks_per_chunk=2000,
    package_as_dataframe=True,
    verbose=True,
    parallel_kwargs=None,
):
    """see fetch_events() for complete kwarg list"""

    # create chunks
    start_block, end_block = block_utils.normalize_block_range(
        start_block=start_block,
        end_block=end_block,
    )
    if verbose:
        print(
            'getting events from node, block range:', [start_block, end_block]
        )
    blocks_per_chunk = min(1000, blocks_per_chunk)
    if blocks_per_chunk is not None:
        chunks = block_utils.get_chunks_in_range(
            start_block=start_block,
            end_block=end_block,
            chunk_size=blocks_per_chunk,
            trim_excess=True,
        )
    else:
        chunks = [[start_block, end_block]]

    # gather metadata
    if contract_abi is None:
        contract_abi = contract_abi_utils.get_contract_abi(
            contract_address=contract_address,
        )
    if event_name is None and event_hash is None:
        raise Exception('must specify event_name or event_hash')
    if event_name is None:
        event_name = contract_abi_utils.get_event_abi(
            event_hash=event_hash,
            contract_abi=contract_abi,
            contract_address=contract_address,
        )['name']
    if event_hash is None:
        event_hash = contract_abi_utils.get_event_hash(
            event_name=event_name,
            contract_abi=contract_abi,
            contract_address=contract_address,
        )

    # fetch events
    chunks_entries = _get_chunk_of_events_from_node(
        block_ranges=chunks,
        event_hash=event_hash,
        contract_address=contract_address,
        verbose=verbose,
        parallel_kwargs=parallel_kwargs,
    )
    entries = [
        entry for chunk_entries in chunks_entries for entry in chunk_entries
    ]

    # package as dataframe
    if package_as_dataframe:
        entries = _package_exported_events(
            entries,
            contract_address=contract_address,
            contract_abi=contract_abi,
            event_hash=event_hash,
            event_name=event_name,
        )

    return entries


@toolparallel.parallelize_input(
    singular_arg='block_range',
    plural_arg='block_ranges',
    config={'n_workers': 60},
)
def _get_chunk_of_events_from_node(
    block_range,
    event_hash,
    contract_address,
    verbose,
):

    if verbose > 1:
        print('scraping block range: ' + str(block_range) + '\n', end='')

    # fetch entries
    start_block, end_block = block_range
    entries = rpc_utils.eth_get_logs(
        contract_address=contract_address,
        topics=[event_hash],
        start_block=start_block,
        end_block=end_block,
    )

    return entries


def _package_exported_events(
    entries, contract_address, contract_abi, event_hash, event_name
):

    if len(entries) == 0:
        return create_empty_event_dataframe(
            contract_address=contract_address,
            contract_abi=contract_abi,
            event_hash=event_hash,
            event_name=event_name,
        )

    formatted_entries = []
    for entry in entries:
        formatted_entry = contract_abi_utils.normalize_event(
            event=entry,
            contract_address=contract_address,
            contract_abi=contract_abi,
            event_name=event_name,
            event_hash=event_hash,
        )
        formatted_entries.append(formatted_entry)

    import pandas as pd
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
        event_abi = contract_abi_utils.get_event_abi(
            contract_address=contract_address,
            contract_abi=contract_abi,
            event_hash=event_hash,
            event_name=event_name,
        )
    for item in event_abi['inputs']:
        columns.append('arg__' + item['name'])

    import pandas as pd
    df = pd.DataFrame(columns=columns)
    df = df.set_index(['block_number', 'transaction_index', 'log_index'])

    return df

