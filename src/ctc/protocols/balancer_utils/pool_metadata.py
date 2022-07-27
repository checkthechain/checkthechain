from __future__ import annotations

from ctc import rpc
from ctc import spec

from . import balancer_spec


async def async_get_pool_id(
    pool_address: spec.Address,
    block: spec.BlockNumberReference | None = None,
) -> str:

    function_abi: spec.FunctionABI = {
        'inputs': [],
        'name': 'getPoolId',
        'outputs': [
            {
                'internalType': 'bytes32',
                'name': '',
                'type': 'bytes32',
            },
        ],
        'stateMutability': 'view',
        'type': 'function',
    }

    result = await rpc.async_eth_call(
        to_address=pool_address,
        function_abi=function_abi,
        block_number=block,
    )
    if not isinstance(result, str):
        raise Exception('invalid rpc result')
    return result


async def async_get_pool_address(
    pool_id: str,
    block: spec.BlockNumberReference | None = None,
) -> spec.Address:

    vault = balancer_spec.vault

    pool = await rpc.async_eth_call(
        to_address=vault,
        function_abi=balancer_spec.vault_function_abis['getPool'],
        function_parameters=[pool_id],
        block_number=block,
    )
    address = pool[0]
    if not isinstance(address, str):
        raise Exception('invalid rpc result')
    return address


async def async_get_pool_tokens(
    *,
    pool_address: spec.Address | None = None,
    pool_id: str | None = None,
    block: spec.BlockNumberReference | None = None,
) -> list[spec.Address]:

    vault = balancer_spec.vault
    if pool_id is None:
        if pool_address is None:
            raise Exception('must specify pool_id or pool_address')
        pool_id = await async_get_pool_id(pool_address)

    pool_tokens = await rpc.async_eth_call(
        to_address=vault,
        function_abi=balancer_spec.vault_function_abis['getPoolTokens'],
        function_parameters=[pool_id],
        block_number=block,
        package_named_outputs=True,
    )
    return list(pool_tokens['tokens'])
