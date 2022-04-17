from __future__ import annotations

from ctc import directory
from ctc import rpc
from ctc import spec


async def async_get_pool_id(
    pool_address: spec.Address,
    block: spec.BlockNumberReference | None = None,
) -> str:
    return await rpc.async_eth_call(
        to_address=pool_address,
        function_name='getPoolId',
        block_number=block,
    )


async def async_get_pool_address(
    pool_id: str,
    block: spec.BlockNumberReference | None = None,
    vault: spec.Address = None,
) -> spec.Address:
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
    *,
    pool_address: spec.Address | None = None,
    pool_id: str | None = None,
    block: spec.BlockNumberReference | None = None,
    vault: spec.Address | None = None,
) -> list[spec.Address]:

    if vault is None:
        vault = directory.get_address(name='Vault', label='balancer')
    if pool_id is None:
        if pool_address is None:
            raise Exception('must specify pool_id or pool_address')
        pool_id = await async_get_pool_id(pool_address)

    pool_tokens = await rpc.async_eth_call(
        to_address=vault,
        function_name='getPoolTokens',
        function_parameters=[pool_id],
        block_number=block,
        package_named_outputs=True,
    )
    return list(pool_tokens['tokens'])

