from __future__ import annotations

import time
import typing

from ctc import evm
from ctc import spec

if typing.TYPE_CHECKING:
    import asyncio
    from typing_extensions import TypedDict

    class LatestBlockCacheEntry(TypedDict, total=False):
        request_time: float
        response_time: float
        block_number: int


async def async_get_block(
    block: spec.BlockReference,
    *,
    include_full_transactions: bool = False,
    context: spec.Context = None,
) -> spec.Block:
    """get block from local database or from RPC node"""

    from ctc import config
    from ctc import rpc

    if spec.is_block_number_reference(block):

        from ctc import db

        read_cache, write_cache = config.get_context_cache_read_write(
            schema_name='blocks', context=context
        )

        if read_cache and not include_full_transactions:
            db_block_data = await db.async_query_block(
                block_number=block,
                context=context,
            )
            if db_block_data is not None:
                return db_block_data

        block_data: spec.Block = await rpc.async_eth_get_block_by_number(
            block_number=evm.standardize_block_number(block),
            context=context,
            include_full_transactions=include_full_transactions,
        )
        block_data.setdefault('base_fee_per_gas', None)

        if write_cache:
            await db.async_intake_block(
                block=block_data,
                context=context,
            )

        return block_data

    elif spec.is_block_hash(block):

        block_data = await rpc.async_eth_get_block_by_hash(
            block_hash=block,
            context=context,
            include_full_transactions=include_full_transactions,
        )
        return block_data

    else:
        raise Exception('unknown block specifier: ' + str(block))


async def async_get_blocks(
    blocks: typing.Sequence[spec.BlockReference],
    *,
    include_full_transactions: bool = False,
    latest_block_number: int | None = None,
    context: spec.Context = None,
) -> list[spec.Block]:
    """get blocks from local database or from RPC node"""

    from ctc import config
    from ctc import rpc

    if all(spec.is_block_number_reference(block) for block in blocks):

        standardized = [evm.standardize_block_number(block) for block in blocks]
        pending = standardized

        read_cache, write_cache = config.get_context_cache_read_write(
            schema_name='blocks', context=context
        )

        if read_cache and not include_full_transactions:
            from ctc import db

            db_block_datas = await db.async_query_blocks(
                block_numbers=pending, context=context
            )
            if db_block_datas is None:
                block_data_map = {}
            else:
                block_data_map = dict(zip(pending, db_block_datas))
                pending = [
                    block
                    for block, db_block_data in block_data_map.items()
                    if db_block_data is None
                ]
        else:
            block_data_map = {}

        blocks_data = await rpc.async_batch_eth_get_block_by_number(
            block_numbers=pending,
            include_full_transactions=include_full_transactions,
            context=context,
        )
        for block_data in blocks_data:
            block_data.setdefault('base_fee_per_gas', None)

        # intake rpc data to db
        if write_cache:
            from ctc import db

            await db.async_intake_blocks(
                blocks=blocks_data,
                latest_block_number=latest_block_number,
                context=context,
            )

            block_data_map.update(dict(zip(pending, blocks_data)))
            blocks_data = [block_data_map[block] for block in standardized]

        return blocks_data

    elif all(spec.is_block_hash(block) for block in blocks):

        return await rpc.async_batch_eth_get_block_by_hash(
            block_hashes=blocks,
            include_full_transactions=include_full_transactions,
            context=context,
        )

    else:
        raise Exception(
            'blocks should be all block number references or all block hashes'
        )


_latest_block_cache: typing.MutableMapping[int, LatestBlockCacheEntry] = {}
_latest_block_lock: typing.MutableMapping[str, asyncio.Lock | None] = {
    'lock': None
}


async def async_get_latest_block_number(
    *,
    context: spec.Context = None,
    use_cache: bool = True,
    cache_time: int | float = 1,
) -> int:
    """get latest block number

    uses a per-network in-memory cache with a ttl of cache_time
    """

    from ctc import config
    from ctc import rpc

    if not use_cache:
        result = await rpc.async_eth_block_number(context=context)
        if not isinstance(result, int):
            raise Exception('invalid rpc result')
        return result

    else:

        # must initialize asyncio.Lock within a running event loop
        # see https://stackoverflow.com/a/55918049
        lock = _latest_block_lock['lock']
        if lock is None:
            import asyncio

            lock = asyncio.Lock()
            _latest_block_lock['lock'] = lock

        async with lock:

            network = config.get_context_chain_id(context)
            request_time = time.time()
            network_cache = _latest_block_cache.get(network)
            if (
                network_cache is not None
                and request_time - network_cache['request_time'] < cache_time
            ):
                return network_cache['block_number']

            result = await rpc.async_eth_block_number(context=context)
            if not isinstance(result, int):
                raise Exception('invalid rpc result')

            response_time = time.time()
            _latest_block_cache[network] = {
                'request_time': request_time,
                'response_time': response_time,
                'block_number': result,
            }

            return result
