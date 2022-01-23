from ctc import rpc

from .. import rari_abis


fuse_directory = '0x835482fe0532f169024d5e9410199369aad5c77e'


async def async_get_all_pools(block='latest'):
    # TODO: convert output to dict
    return await rpc.async_eth_call(
        to_address=fuse_directory,
        block_number=block,
        function_abi=rari_abis.pool_directory_abis['getAllPools'],
    )

