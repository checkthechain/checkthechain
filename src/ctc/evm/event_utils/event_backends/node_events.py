import asyncio

from ctc import rpc
from ctc import binary
from ... import abi_utils
from ... import block_utils


async def async_get_events_from_node(
    start_block='latest',
    end_block='latest',
    event_name=None,
    event_hash=None,
    event_abi=None,
    contract_address=None,
    contract_abi=None,
    blocks_per_chunk=2000,
    package_as_dataframe=True,
    verbose=True,
):
    """see fetch_events() for complete kwarg list"""

    # create chunks
    start_block, end_block = await block_utils.async_block_numbers_to_int(
        blocks=[start_block, end_block],
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
    if contract_abi is None and event_abi is None:
        contract_abi = await abi_utils.async_get_contract_abi(
            contract_address=contract_address,
        )
    if event_name is None and event_hash is None and event_abi is None:
        raise Exception('must specify event_name or event_hash or event_abi')
    if event_name is None:
        if event_abi is None:
            event_abi = await abi_utils.async_get_event_abi(
                event_hash=event_hash,
                contract_abi=contract_abi,
                contract_address=contract_address,
            )
        event_name = event_abi['name']
    if event_hash is None:
        if event_abi is None:
            event_abi = await abi_utils.async_get_event_abi(
                event_hash=event_hash,
                contract_abi=contract_abi,
                contract_address=contract_address,
            )
        if event_name is not None:
            event_hash = binary.get_event_hash(event_abi=event_abi)
        elif event_abi is not None:
            event_hash = contract_address.get_event_hash(event_abi=event_abi)

        else:
            raise Exception('must specify event_name, event_abi, or event_hash')

    # fetch events
    coroutines = []
    for chunk in chunks:
        coroutine = await _async_get_chunk_of_events_from_node(
            block_range=chunk,
            event_hash=event_hash,
            contract_address=contract_address,
            verbose=verbose,
        )
        coroutines.append(coroutine)
    chunks_entries = await asyncio.gather(*coroutines)
    entries = [
        entry for chunk_entries in chunks_entries for entry in chunk_entries
    ]

    # package as dataframe
    if package_as_dataframe:
        entries = _async_package_exported_events(
            entries,
            contract_address=contract_address,
            contract_abi=contract_abi,
            event_hash=event_hash,
            event_name=event_name,
            event_abi=event_abi,
        )

    return entries


async def _async_get_chunk_of_events_from_node(
    block_range,
    event_hash,
    contract_address,
    verbose,
):

    if verbose > 1:
        print('scraping block range: ' + str(block_range) + '\n', end='')

    # fetch entries
    start_block, end_block = block_range
    entries = await rpc.async_eth_get_logs(
        contract_address=contract_address,
        topics=[event_hash],
        start_block=start_block,
        end_block=end_block,
    )

    return entries


async def _package_exported_events(
    entries, contract_address, contract_abi, event_hash, event_name, event_abi
):
    if event_abi is None:
        event_abi = await binary.async_get_event_abi(
            contract_address=contract_address,
            contract_abi=contract_abi,
            event_hash=event_hash,
            event_name=event_name,
        )

    if len(entries) == 0:
        return create_empty_event_dataframe(event_abi=event_abi)

    formatted_entries = []
    for entry in entries:
        formatted_entry = binary.normalize_event(
            event=entry,
            contract_abi=contract_abi,
        )
        formatted_entries.append(formatted_entry)

    import pandas as pd

    df = pd.DataFrame(formatted_entries)
    df = df.set_index(['block_number', 'transaction_index', 'log_index'])

    return df


def create_empty_event_dataframe(
    event_abi=None,
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
    for item in event_abi['inputs']:
        columns.append('arg__' + item['name'])

    import pandas as pd

    df = pd.DataFrame(columns=columns)
    df = df.set_index(['block_number', 'transaction_index', 'log_index'])

    return df

