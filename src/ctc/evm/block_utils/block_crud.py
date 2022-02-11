from __future__ import annotations

from ctc import rpc
from ctc import spec
from . import block_normalize


async def async_get_block(
    block: spec.BlockReference,
    include_full_transactions: bool = False,
    provider: spec.ProviderSpec = None,
) -> spec.Block:

    if spec.is_block_number_reference(block):

        return await rpc.async_eth_get_block_by_number(
            block_number=block_normalize.standardize_block_number(block),
            provider=provider,
            include_full_transactions=include_full_transactions,
        )

    elif spec.is_block_hash(block):

        return await rpc.async_eth_get_block_by_hash(
            block_hash=block,
            provider=provider,
            include_full_transactions=include_full_transactions,
        )

    else:
        raise Exception('unknown block specifier: ' + str(block))


async def async_get_blocks(
    blocks: list[spec.BlockReference],
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
    blocks: list[spec.BlockReference], **get_blocks_kwargs
) -> list[int]:
    return [
        block['timestamp']
        for block in await async_get_blocks(blocks=blocks, **get_blocks_kwargs)
    ]

