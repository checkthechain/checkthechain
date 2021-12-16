import typing

import toolparallel

from ctc import rpc
from ctc import spec
from .. import rpc_utils
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
) -> spec.Block:

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


#
# # old
#


@toolparallel.parallelize_input(singular_arg='block', plural_arg='blocks')
def get_block(
    block, provider=None, include_full_transactions=False, **rpc_kwargs
):

    # convert to int if not an int or str (e.g. floats or numpy int32)
    if not isinstance(block, (int, str)):
        candidate = int(block)
        if (block - candidate) ** 2 ** 0.5 > 0.001:
            raise Exception()
        block = candidate

    # gather kwargs
    kwargs = dict(
        provider=provider,
        include_full_transactions=include_full_transactions,
        **rpc_kwargs
    )

    # rpc call
    if isinstance(block, int):
        return rpc_utils.eth_get_block_by_number(block_number=block, **kwargs)
    elif isinstance(block, str):
        if block in ['latest', 'earliest', 'pending']:
            return rpc_utils.eth_get_block_by_number(
                block_number=block, **kwargs
            )
        elif block.startswith('0x'):
            if len(block) == 66:
                return rpc_utils.eth_get_block_by_hash(
                    block_hash=block, **kwargs
                )
            else:
                return rpc_utils.eth_get_block_by_number(
                    block_number=block, **kwargs
                )
        elif len(block) == 64:
            return rpc_utils.eth_get_block_by_hash(block_hash=block, **kwargs)
        elif str.isnumeric(block):
            return rpc_utils.eth_get_block_by_number(
                block_number=int(block), **kwargs
            )
        else:
            raise Exception('unknown block str format: ' + str(block))
    else:
        raise Exception('unknown block specifier: ' + str(block))


def get_blocks(blocks):

    rpc_request = [
        rpc_utils.construct_eth_get_block_by_number(
            block_number=int(block),
            include_full_transactions=False,
        )
        for block in blocks
    ]

    return rpc_utils.rpc_execute(rpc_request=rpc_request)


def get_blocks_timestamps(blocks):
    return {block['number']: block['timestamp'] for block in get_blocks(blocks)}


def get_block_number(block, provider=None, **rpc_kwargs):

    # gather kwargs
    kwargs = dict(provider=provider, **rpc_kwargs)

    # rpc call
    if block == 'latest':
        return rpc_utils.eth_block_number(**kwargs)
    else:
        return get_block(block=block, **kwargs)['number']

