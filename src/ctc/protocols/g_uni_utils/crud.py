from __future__ import annotations

import asyncio
import typing

from ctc import rpc
from ctc import evm
from ctc import spec


guni_function_abis = {
    'token0': {
        'constant': True,
        'inputs': [],
        'name': 'token0',
        'outputs': [{'internalType': 'address', 'name': '', 'type': 'address'}],
        'payable': False,
        'stateMutability': 'view',
        'type': 'function',
    },
    'token1': {
        'constant': True,
        'inputs': [],
        'name': 'token1',
        'outputs': [{'internalType': 'address', 'name': '', 'type': 'address'}],
        'payable': False,
        'stateMutability': 'view',
        'type': 'function',
    },
}


async def async_get_tokens(
    g_uni_pool: spec.Address,
    *,
    context: spec.Context = None,
) -> tuple[spec.Address, spec.Address]:
    return await asyncio.gather(
        rpc.async_eth_call(
            to_address=g_uni_pool, function_name='token0', context=context
        ),
        rpc.async_eth_call(
            to_address=g_uni_pool, function_name='token1', context=context
        ),
    )


async def async_get_token_balances(
    g_uni_pool: spec.Address,
    *,
    normalize: bool = True,
    context: spec.Context = None,
) -> typing.Sequence[int | float]:
    balances_coroutine = rpc.async_eth_call(
        to_address=g_uni_pool,
        function_name='getUnderlyingBalances',
        context=context,
    )
    balances_task = asyncio.create_task(balances_coroutine)

    if normalize:
        tokens_coroutine = async_get_tokens(
            g_uni_pool,
            context=context,
        )
        tokens_task = asyncio.create_task(tokens_coroutine)

        return await evm.async_normalize_erc20s_quantities(
            quantities=(await balances_task),
            tokens=(await tokens_task),
            context=context,
        )

    else:

        result = await balances_task
        if not isinstance(result, (tuple, list)) or not all(
            isinstance(item, int) for item in result
        ):
            raise Exception('invalid rpc result')
        return result


async def async_get_token_balances_by_block(
    g_uni_pool: spec.Address,
    blocks: typing.Sequence[spec.BlockNumberReference],
    *,
    normalize: bool = True,
    context: spec.Context = None,
) -> typing.Sequence[typing.Sequence[int | float]]:
    balances_coroutine = rpc.async_batch_eth_call(
        to_address=g_uni_pool,
        function_name='getUnderlyingBalances',
        block_numbers=blocks,
        context=context,
    )
    balances_task = asyncio.create_task(balances_coroutine)

    if normalize:
        tokens_coroutine = async_get_tokens(g_uni_pool, context=context)
        tokens_task = asyncio.create_task(tokens_coroutine)

        balances = await balances_task
        token0_balances, token1_balances = list(zip(*balances))

        # normalize
        tokens = await tokens_task
        token0_coroutine = evm.async_normalize_erc20_quantities_by_block(
            quantities=token0_balances,
            token=tokens[0],
            blocks=blocks,
            context=context,
        )
        token1_coroutine = evm.async_normalize_erc20_quantities_by_block(
            quantities=token1_balances,
            token=tokens[1],
            blocks=blocks,
            context=context,
        )
        token0_task = asyncio.create_task(token0_coroutine)
        token1_task = asyncio.create_task(token1_coroutine)

        result = await asyncio.gather(token0_task, token1_task)
        return list(list(item) for item in zip(*result))

    else:
        return await balances_task

