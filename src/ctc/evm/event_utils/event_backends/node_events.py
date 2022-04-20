from __future__ import annotations

import asyncio
import typing

from ctc import binary
from ctc import rpc
from ctc import spec

from ... import abi_utils
from ... import block_utils


async def async_get_events_from_node(
    start_block: spec.BlockNumberReference = 'latest',
    end_block: spec.BlockNumberReference = 'latest',
    event_name: str | None = None,
    event_hash: str | None = None,
    event_abi: spec.EventABI | None = None,
    contract_address: spec.Address | None = None,
    contract_abi: spec.ContractABI | None = None,
    blocks_per_chunk: int = 2000,
    verbose: bool = True,
    provider: spec.ProviderSpec = None,
) -> spec.DataFrame:
    """see fetch_events() for complete kwarg list"""

    provider = rpc.get_provider(provider)
    network = provider['network']
    if network is None:
        raise Exception('could not determine network')

    # create chunks
    start_block, end_block = await block_utils.async_block_numbers_to_int(
        blocks=[start_block, end_block],
        provider=provider,
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
            network=network,
        )
    if event_name is None and event_hash is None and event_abi is None:
        raise Exception('must specify event_name or event_hash or event_abi')
    if event_name is None:
        if event_abi is None:
            event_abi = await abi_utils.async_get_event_abi(
                event_hash=event_hash,
                contract_abi=contract_abi,
                contract_address=contract_address,
                network=network,
            )
        event_name = event_abi['name']
    if event_hash is None:
        if event_abi is None:
            event_abi = await abi_utils.async_get_event_abi(
                event_hash=event_hash,
                event_name=event_name,
                contract_abi=contract_abi,
                contract_address=contract_address,
                network=network,
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
        coroutine = _async_get_chunk_of_events_from_node(
            block_range=chunk,
            event_hash=event_hash,
            contract_address=contract_address,
            verbose=verbose,
            provider=provider,
        )
        coroutines.append(coroutine)
    chunks_entries = await asyncio.gather(*coroutines)
    entries = [
        entry for chunk_entries in chunks_entries for entry in chunk_entries
    ]

    # package as dataframe
    return await _async_package_exported_events(
        entries,
        contract_address=contract_address,
        contract_abi=contract_abi,
        event_hash=event_hash,
        event_name=event_name,
        event_abi=event_abi,
        provider=provider,
    )


async def _async_get_chunk_of_events_from_node(
    block_range: typing.Sequence[spec.BlockNumberReference],
    event_hash: str,
    contract_address: spec.Address | None,
    verbose: bool,
    provider: spec.ProviderSpec = None,
) -> typing.Sequence[spec.RawLog]:

    if verbose > 1:
        print('scraping block range: ' + str(block_range) + '\n', end='')

    # fetch entries
    start_block, end_block = block_range
    start_block = binary.standardize_block_number(start_block)
    end_block = binary.standardize_block_number(end_block)
    entries = await rpc.async_eth_get_logs(
        address=contract_address,
        topics=[event_hash],
        start_block=start_block,
        end_block=end_block,
        provider=provider,
    )

    return entries


async def _async_package_exported_events(
    entries: typing.Sequence[spec.RawLog],
    contract_address: spec.Address | None,
    contract_abi: spec.ContractABI | None,
    event_hash: str,
    event_name: str,
    event_abi: spec.EventABI | None,
    provider: spec.ProviderSpec,
) -> spec.DataFrame:

    if event_abi is None:
        network = rpc.get_provider_network(provider)
        event_abi = await abi_utils.async_get_event_abi(
            contract_address=contract_address,
            contract_abi=contract_abi,
            event_hash=event_hash,
            event_name=event_name,
            network=network,
        )

    if len(entries) == 0:
        return create_empty_event_dataframe(event_abi=event_abi)

    formatted_entries = []
    for entry in entries:
        formatted_entry = binary.normalize_event(
            event=entry,
            event_abi=event_abi,
        )
        formatted_entries.append(formatted_entry)

    import pandas as pd

    df = pd.DataFrame(formatted_entries)
    df = df.set_index(['block_number', 'transaction_index', 'log_index'])

    return df


def create_empty_event_dataframe(
    event_abi: spec.EventABI | None = None,
) -> spec.DataFrame:

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
    if event_abi is not None:
        for item in event_abi['inputs']:
            columns.append('arg__' + item['name'])

    import pandas as pd

    df = pd.DataFrame(columns=columns)
    df = df.set_index(['block_number', 'transaction_index', 'log_index'])

    return df

