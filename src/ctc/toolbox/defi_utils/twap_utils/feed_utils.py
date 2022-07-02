from __future__ import annotations

import asyncio
import typing

from ctc import rpc
from ctc import spec


def get_contract_type_guards() -> dict[
    str,
    typing.Callable[..., typing.Coroutine[typing.Any, typing.Any, bool]],
]:
    return {
        'chainlink_feed': async_is_chainlink_feed,
        'uniswap_v2_pool': async_is_uniswap_v2_pool,
        'uniswap_v3_pool': async_is_uniswap_v3_pool,
        'curve_pool': async_is_curve_pool,
        'sushi_pool': async_is_sushi_pool,
        'balancer_v2_pool': async_is_balancer_v2_pool,
    }


async def async_get_contract_type(
    address: spec.Address,
    provider: spec.ProviderReference = None,
) -> str:

    contract_guards = get_contract_type_guards()
    coroutines = [
        contract_guard(address=address, provider=provider)
        for contract_guard in contract_guards.values()
    ]
    tasks = [asyncio.create_task(coroutine) for coroutine in coroutines]
    contract_guard_names = list(contract_guards.keys())
    while True:
        done, pending = await asyncio.wait(
            tasks,
            return_when=asyncio.FIRST_COMPLETED,
        )
        for task in done:
            result = task.result()
            if result:
                return contract_guard_names[tasks.index(task)]
        if len(pending) == 0:
            raise Exception('could not determine contract type')


#
# # specific guard
#


async def async_is_chainlink_feed(
    address: spec.Address, provider: spec.ProviderReference = None
) -> bool:
    try:
        await rpc.async_eth_call(
            to_address=address,
            function_abi={'name': 'aggregator', 'inputs': [], 'outputs': []},
            provider=provider,
        )
        return True
    except spec.RpcException:
        return False


async def async_is_uniswap_v2_pool(
    address: spec.Address, provider: spec.ProviderReference = None
) -> bool:
    try:
        factory = await rpc.async_eth_call(
            to_address=address,
            function_abi={
                'name': 'factory',
                'inputs': [],
                'outputs': [{'type': 'address'}],
            },
            provider=provider,
        )
        return bool(factory == '0x5c69bee701ef814a2b6a3edd4b1652cb9cc5aa6f')
    except spec.RpcException:
        return False


async def async_is_uniswap_v3_pool(
    address: spec.Address, provider: spec.ProviderReference = None
) -> bool:
    try:
        factory = await rpc.async_eth_call(
            to_address=address,
            function_abi={
                'name': 'factory',
                'inputs': [],
                'outputs': [{'type': 'address'}],
            },
            provider=provider,
        )
        return bool(factory == '0x1f98431c8ad98523631ae4a59f267346ea31f984')
    except spec.RpcException:
        return False


async def async_is_curve_pool(
    address: spec.Address, provider: spec.ProviderReference = None
) -> bool:
    # doesn't work for early pools
    try:
        await rpc.async_eth_call(
            to_address=address,
            function_abi={'name': 'A', 'inputs': [], 'outputs': []},
            provider=provider,
        )
        return True
    except spec.RpcException:
        return False


async def async_is_sushi_pool(
    address: spec.Address, provider: spec.ProviderReference = None
) -> bool:
    try:
        factory = await rpc.async_eth_call(
            to_address=address,
            function_abi={
                'name': 'factory',
                'inputs': [],
                'outputs': [{'type': 'address'}],
            },
            provider=provider,
        )
        return bool(factory == '0xc0aee478e3658e2610c5f7a4a2e1777ce9e4f2ac')
    except spec.RpcException:
        return False


async def async_is_balancer_v2_pool(
    address: spec.Address, provider: spec.ProviderReference = None
) -> bool:
    try:
        await rpc.async_eth_call(
            to_address=address,
            function_abi={'name': 'getPoolId', 'inputs': [], 'outputs': []},
            provider=provider,
        )
        return True
    except spec.RpcException:
        return False
