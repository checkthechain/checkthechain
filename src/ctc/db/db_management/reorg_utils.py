"""
- revalidation after a reorg is expensive
- should use a large enough confirmation time to make reorgs rare
"""

from __future__ import annotations

import asyncio
import typing

import toolsql
import tooltime

from ctc import evm
from ctc import rpc
from ctc import spec
from .. import db_schemas


def get_required_confirmations(network: spec.NetworkReference) -> int:
    # for now use single confirmation age for all datatypes and networks
    return 128


async def async_revalidate_blocks(
    conn: toolsql.SAConnection,
    start_block: spec.BlockNumberReference | None = None,
    start_time: tooltime.Timestamp | None = None,
    end_block: spec.BlockNumberReference | None = None,
    end_time: tooltime.Timestamp | None = None,
    provider: spec.ProviderSpec | None = None,
) -> typing.Mapping:

    if start_block is not None and start_time is not None:
        raise Exception('cannot specify both start_block and start_time')
    if start_block is None:
        if start_time is None:
            start_block = 0
        else:
            start_block_number = await evm.async_get_block_of_timestamp(
                timestamp=start_time,
                provider=provider,
            )
            start_block_data = await evm.async_get_block(start_block_number)
            start_block = start_block_data['number']
    if end_block is not None and end_time is not None:
        raise Exception('cannot specify both end_block and end_time')
    if end_block is None:
        if end_time is None:
            end_block = 0
        else:
            end_block_number = await evm.async_get_block_of_timestamp(
                timestamp=end_time,
                provider=provider,
            )
            end_block_data = await evm.async_get_block(end_block_number)
            end_block = end_block_data['number']

    # get network
    network = rpc.get_provider_network(provider)
    table_name = db_schemas.get_table_name(
        table_name='blocks',
        network=network,
    )

    # build query
    query_kwargs: toolsql.SelectQuery = {
        'table': table_name,
        'only_columns': ['block_number', 'hash'],
    }
    if start_block is not None:
        query_kwargs['where_gte'] = {'block_number': start_block}
    if end_block is not None:
        query_kwargs['where_lte'] = {'block_number': end_block}

    # get blocks from database
    db_blocks = toolsql.select(
        conn=conn,
        **query_kwargs,
    )

    # check that the db hashes match the hashes from rpc provider
    coroutines = [
        async_does_block_hash_match(item['block_number'], item['block_hash'])
        for item in db_blocks
    ]
    matches = await asyncio.gather(*coroutines)
    invalid_blocks = [
        item for match, item in zip(matches, db_blocks) if not match
    ]

    return {
        'block_range': [start_block, end_block],
        'invalid_blocks': invalid_blocks,
    }


async def async_get_premature_blocks(
    conn: toolsql.SAConnection,
    provider: spec.ProviderSpec = None,
) -> typing.Mapping:
    # get network
    network = rpc.get_provider_network(provider)
    table_name = db_schemas.get_table_name(
        table_name='blocks', network=network
    )
    network = rpc.get_provider_network(provider)

    # blocks that are younger than confirmation age
    latest_block_number = await evm.async_get_latest_block_number(
        provider=provider
    )
    min_confirmations = get_required_confirmations(network=network)
    youngest_valid_block = latest_block_number - min_confirmations

    n_premature_blocks = toolsql.select(
        conn=conn,
        table=table_name,
        where_gte={'block_number': youngest_valid_block},
        # count=True,
    )

    return {
        'latest_rpc_block': latest_block_number,
        'min_confirmations': min_confirmations,
        'youngest_valid_block': youngest_valid_block,
        'n_premature_blocks': n_premature_blocks,
    }


async def async_clean_invalid_blocks() -> None:
    raise NotImplementedError()


async def async_does_block_hash_match(
    block_number: int,
    block_hash: str,
) -> None:
    raise NotImplementedError()


async def async_detect_block_reorgs(
    conn: toolsql.SAConnection,
    check_block_number: spec.BlockNumberReference = 'latest',
    provider: spec.ProviderSpec = None,
) -> None:
    # detect
    check_block = await evm.async_get_block(check_block_number, provider=provider)
    block_number = check_block['number']

    # if block_db.has_block(block_number=block_number):
    #     pass


# def detect_event_reorgs() -> None:
#     # assumes that
#     start_block = events.get_event_data(columns['block_number'])
#     block_hashes = events.get_event_data(columns=['block_hash'], unique=True)

