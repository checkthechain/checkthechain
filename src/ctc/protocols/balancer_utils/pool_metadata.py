from __future__ import annotations

import ast
import typing

from ctc import evm
from ctc import rpc
from ctc import spec

from . import balancer_spec

if typing.TYPE_CHECKING:
    import tooltime


async def async_get_pool_id(
    pool_address: spec.Address,
    block: spec.BlockNumberReference | None = None,
    *,
    provider: spec.ProviderReference | None = None,
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
        provider=provider,
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


async def async_get_token_registrations(
    factory: spec.Address,
    *,
    start_block: spec.BlockNumberReference | None = None,
    end_block: spec.BlockNumberReference | None = None,
    start_time: tooltime.Timestamp | None = None,
    end_time: tooltime.Timestamp | None = None,
    provider: spec.ProviderReference = None,
) -> typing.Mapping[str, typing.Sequence[str]]:

    balancer_token_registrations = await evm.async_get_events(
        factory,
        event_abi=balancer_spec.vault_event_abis['TokensRegistered'],
        verbose=False,
        start_block=start_block,
        end_block=end_block,
        start_time=start_time,
        end_time=end_time,
        provider=provider,
    )
    balancer_token_registrations['arg__tokens'] = balancer_token_registrations[
        'arg__tokens'
    ].map(ast.literal_eval)

    token_registrations_by_pool: typing.MutableMapping[
        str, typing.MutableSequence[str]
    ] = {}
    for index, row in balancer_token_registrations.iterrows():
        pool = row['arg__poolId']

        token_registrations_by_pool.setdefault(pool, [])
        token_registrations_by_pool[pool].extend(row['arg__tokens'])

    return token_registrations_by_pool
