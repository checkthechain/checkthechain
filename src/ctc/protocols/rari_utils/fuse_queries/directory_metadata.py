from __future__ import annotations

from ctc import rpc
from ctc import spec

import typing

from .. import rari_abis


fuse_directory = '0x835482fe0532f169024d5e9410199369aad5c77e'


async def async_get_all_pools(
    block: typing.Optional[spec.BlockNumberReference] = None,
    provider: spec.ProviderSpec = None,
) -> list[list[typing.Any]]:

    # TODO: convert output to dict
    return await rpc.async_eth_call(
        to_address=fuse_directory,
        block_number=block,
        function_abi=rari_abis.pool_directory_abis['getAllPools'],
        provider=provider,
    )

