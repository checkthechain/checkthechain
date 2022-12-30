from __future__ import annotations

import typing

from .. import abi_utils
from .. import block_utils
from ctc import spec


async def async_get_event_timestamps(
    events: spec.DataFrame,
    context: spec.Context = None,
) -> typing.Sequence[int]:
    """get timestamps of an events dataframe"""

    # get block_numbers
    multi_index = 'block_number' in events.index.names
    if multi_index:
        block_numbers: typing.Sequence[int] = typing.cast(
            typing.Sequence[int],
            events.index.get_level_values('block_number'),
        )
    else:
        block_numbers = typing.cast(
            typing.Sequence[int],
            events.index.values,
        )

    # get timestamps
    return await block_utils.async_get_block_timestamps(
        block_numbers,
        context=context,
    )


async def _async_get_event_names_column(
    events: spec.DataFrame,
    *,
    share_abis_across_contracts: bool = True,
    context: spec.Context = None,
) -> typing.Sequence[str]:

    # compile which event abis are needed
    event_abi_queries = {}
    for contract_address, event_hash in zip(
        events['contract_address'], events['event_hash']
    ):

        if share_abis_across_contracts:
            key = event_hash
        else:
            key = (contract_address, event_hash)

        if key not in event_abi_queries:
            event_abi_queries[key] = {
                'contract_address': contract_address,
                'event_hash': event_hash,
            }

    # get event abis
    event_abis = {}
    for key, query in event_abi_queries.items():
        event_abis[key] = await abi_utils.async_get_event_abi(
            context=context, **query
        )

    # construct column
    event_abi_column = []
    for contract_address, event_hash in zip(
        events['contract_address'].values,
        events['event_hash'].values,
    ):

        if share_abis_across_contracts:
            key = event_hash
        else:
            key = (contract_address, event_hash)

        event_abi_column.append(event_abis[key].get('name', ''))

    return event_abi_column

