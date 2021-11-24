import asyncio

from ctc import rpc
from ctc.protocols import rari_utils


def get_command_spec():
    return {
        'f': fuse_command,
        'options': [
            {'name': 'pool', 'kwargs': {'nargs': '?'}},
            {'name': '--block', 'kwargs': {'default': 'latest'}},
        ],
    }


def fuse_command(pool, block, **kwargs):
    if block != 'latest':
        block = int(block)

    if pool is not None:
        pool_index = int(pool)
        asyncio.run(summarize_fuse_pool(pool_index=pool_index, block=block))

    else:
        asyncio.run(summarize_all_fuse_pools(block=block))


async def summarize_fuse_pool(pool_index, block):
    all_pools = await rari_utils.async_get_all_pools(block=block)
    pool = all_pools[pool_index]
    comptroller = pool[2]
    block_data = await rpc.async_eth_get_block_by_number(block_number=block)

    tokens_data = await rari_utils.async_get_pool_summary_data(
        comptroller=comptroller,
        block=block,
    )
    pool_name = await rari_utils.async_get_pool_name(comptroller=comptroller)
    rari_utils.print_fuse_pool_summary(
        block=block_data,
        tokens_data=tokens_data,
        pool_name=pool_name,
    )

    from ctc.rpc.rpc_backends import rpc_http_async
    provider = rpc.get_provider()
    await rpc_http_async.async_close_session(provider=provider)


async def summarize_all_fuse_pools(block):

    await rari_utils.print_all_pool_summary(block=block)

    from ctc.rpc.rpc_backends import rpc_http_async
    provider = rpc.get_provider()
    await rpc_http_async.async_close_session(provider=provider)

