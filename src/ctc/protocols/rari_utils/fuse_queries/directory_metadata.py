from __future__ import annotations

from ctc import rpc
from ctc import spec

import typing

from .. import rari_abis


fuse_directory = '0x835482fe0532f169024d5e9410199369aad5c77e'


async def async_get_all_pools(
    block: typing.Optional[spec.BlockNumberReference] = None,
    provider: spec.ProviderReference = None,
) -> typing.Sequence[typing.Sequence[typing.Any]]:

    # TODO: convert output to dict
    result = await rpc.async_eth_call(
        to_address=fuse_directory,
        block_number=block,
        function_abi=rari_abis.pool_directory_function_abis['getAllPools'],
        provider=provider,
    )
    if not isinstance(result, (list, tuple)) or not all(
        isinstance(item, (list, tuple)) for item in result
    ):
        raise Exception('invalid rpc result')
    return result
