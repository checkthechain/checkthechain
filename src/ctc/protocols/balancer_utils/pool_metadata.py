from ctc import directory
from ctc import rpc


async def async_get_pool_id(pool_address, block=None):
    return await rpc.async_eth_call(
        to_address=pool_address,
        function_name='getPoolId',
        block_number=block,
    )


async def async_get_pool_address(pool_id, block=None, vault=None):
    if vault is None:
        vault = directory.get_address(name='Vault', label='balancer')

    pool = await rpc.async_eth_call(
        to_address=vault,
        function_name='getPool',
        function_parameters=[pool_id],
        block_number=block,
    )
    return pool[0]


async def async_get_pool_tokens(
    *, pool_address=None, pool_id=None, block=None, vault=None
):

    if vault is None:
        vault = directory.get_address(name='Vault', label='balancer')
    if pool_id is None:
        pool_id = await async_get_pool_id(pool_address)

    pool_tokens = await rpc.async_eth_call(
        to_address=vault,
        function_name='getPoolTokens',
        function_parameters=[pool_id],
        block_number=block,
        package_named_outputs=True,
    )
    return list(pool_tokens['tokens'])

