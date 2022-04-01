from __future__ import annotations

import typing

from ctc import rpc
from ctc import spec
from . import block_normalize


async def async_get_block(
    block: spec.BlockReference,
    include_full_transactions: bool = False,
    provider: spec.ProviderSpec = None,
) -> spec.Block:

    if spec.is_block_number_reference(block):

        block_data = await rpc.async_eth_get_block_by_number(
            block_number=block_normalize.standardize_block_number(block),
            provider=provider,
            include_full_transactions=include_full_transactions,
        )

        await _async_handle_block_storage(block=block_data, provider=provider)

        return block_data

    elif spec.is_block_hash(block):

        return await rpc.async_eth_get_block_by_hash(
            block_hash=block,
            provider=provider,
            include_full_transactions=include_full_transactions,
        )

    else:
        raise Exception('unknown block specifier: ' + str(block))


async def _async_handle_block_storage(block, provider=None):
    from ctc import db

    # determine whether to store block
    network = rpc.get_provider_network(provider=provider)
    min_confirmations = db.get_min_confirmations(
        datatype='block_timestamps',
        network=network,
    )
    engine = db.create_engine(
        datatype='block_timestamps',
        network=network,
    )
    check_if_exists = False
    with engine.connect() as conn:
        if (
            check_if_exists
            and db.get_block_timestamp(conn=conn, block_number=block['number'])
            is not None
        ):
            store = False
        else:
            max_block = db.get_max_block_number(conn=conn, network=network)
            if block['number'] <= max_block - min_confirmations:
                store = True
            else:
                latest_block = await async_get_latest_block_number(
                    provider=provider
                )
                store = block['number'] <= latest_block - min_confirmations

    # store data in db
    if store:
        engine = db.create_engine(
            datatype='block_timestamps',
            network=network,
        )
        with engine.begin() as conn:
            db.set_block_timestamp(
                conn=conn,
                block_number=block['number'],
                timestamp=block['timestamp'],
            )


async def async_get_blocks(
    blocks: typing.Sequence[spec.BlockReference],
    include_full_transactions: bool = False,
    chunk_size: int = 500,
    provider: spec.ProviderSpec = None,
) -> list[spec.Block]:

    provider = rpc.add_provider_parameters(provider, {'chunk_size': chunk_size})

    if all(spec.is_block_number_reference(block) for block in blocks):

        standardized = [
            block_normalize.standardize_block_number(block) for block in blocks
        ]

        return await rpc.async_batch_eth_get_block_by_number(
            block_numbers=standardized,
            include_full_transactions=include_full_transactions,
            provider=provider,
        )

    elif all(spec.is_block_hash(block) for block in blocks):

        return await rpc.async_batch_eth_get_block_by_number(
            block_hashes=blocks,
            include_full_transactions=include_full_transactions,
            provider=provider,
        )

    else:
        raise Exception(
            'blocks should be all block number references or all block hashes'
        )


async def async_get_latest_block_number(
    provider: spec.ProviderSpec = None,
) -> int:
    return await rpc.async_eth_block_number(provider=provider)


async def async_get_blocks_timestamps(
    blocks: typing.Sequence[spec.BlockReference],
    include_full_transactions: bool = False,
    chunk_size: int = 500,
    provider: spec.ProviderSpec = None,
) -> list[int]:
    return [
        block['timestamp']
        for block in await async_get_blocks(
            blocks=blocks,
            include_full_transactions=include_full_transactions,
            chunk_size=chunk_size,
            provider=provider,
        )
    ]

