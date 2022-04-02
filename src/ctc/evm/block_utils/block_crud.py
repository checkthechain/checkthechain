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

        from ctc import db
        await db.async_intake_block(block=block_data, provider=provider)

        return block_data

    elif spec.is_block_hash(block):

        return await rpc.async_eth_get_block_by_hash(
            block_hash=block,
            provider=provider,
            include_full_transactions=include_full_transactions,
        )

    else:
        raise Exception('unknown block specifier: ' + str(block))


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

        blocks_data = await rpc.async_batch_eth_get_block_by_number(
            block_numbers=standardized,
            include_full_transactions=include_full_transactions,
            provider=provider,
        )

        from ctc import db
        await db.async_intake_blocks(blocks=blocks_data, provider=provider)

        return blocks_data

    elif all(spec.is_block_hash(block) for block in blocks):

        return await rpc.async_batch_eth_get_block_by_hash(
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
    use_db: bool = True,
) -> list[int]:

    # get timestamps from db
    if use_db:
        from ctc import db
        network = rpc.get_provider_network(provider)
        engine = db.create_engine(datatype='block_timestamps', network=network)
        with engine.connect() as conn:
            db_timestamps = db.get_blocks_timestamps(
                conn=conn,
                block_numbers=blocks,
            )
        results = dict(zip(blocks, db_timestamps))
        remaining_blocks = [block for block in blocks if block is None]
    else:
        results = {}
        remaining_blocks = blocks

    # get timestamps from rpc
    if len(remaining_blocks) > 0:
        node_blocks = await async_get_blocks(
            blocks=remaining_blocks,
            include_full_transactions=include_full_transactions,
            chunk_size=chunk_size,
            provider=provider,
        )
        for block_data in node_blocks:
            results[block_data['number']] = block_data['timestamp']

    return [results[block] for block in blocks]

