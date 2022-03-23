import asyncio

from ctc import rpc
from ctc import evm


async def async_get_tokens(g_uni_pool):
    return await asyncio.gather(
        rpc.async_eth_call(to_address=g_uni_pool, function_name='token0'),
        rpc.async_eth_call(to_address=g_uni_pool, function_name='token1'),
    )


async def async_get_token_balances(g_uni_pool, normalize=True):
    balances_coroutine = rpc.async_eth_call(
        to_address=g_uni_pool,
        function_name='getUnderlyingBalances',
    )
    balances_task = asyncio.create_task(balances_coroutine)

    if normalize:
        tokens_coroutine = async_get_tokens(g_uni_pool)
        tokens_task = asyncio.create_task(tokens_coroutine)

        return await evm.async_normalize_erc20s_quantities(
            quantities=(await balances_task),
            tokens=(await tokens_task),
        )

    else:

        return await balances_task


async def async_get_token_balances_by_block(g_uni_pool, blocks, normalize=True):
    balances_coroutine = rpc.async_batch_eth_call(
        to_address=g_uni_pool,
        function_name='getUnderlyingBalances',
        block_numbers=blocks,
    )
    balances_task = asyncio.create_task(balances_coroutine)

    if normalize:
        tokens_coroutine = async_get_tokens(g_uni_pool)
        tokens_task = asyncio.create_task(tokens_coroutine)

        balances = await balances_task
        token0_balances, token1_balances = list(zip(*balances))

        # normalize
        tokens = await tokens_task
        token0_coroutine = evm.async_normalize_erc20_quantities_by_block(
            quantities=token0_balances,
            token=tokens[0],
            blocks=blocks,
        )
        token1_coroutine = evm.async_normalize_erc20_quantities_by_block(
            quantities=token1_balances,
            token=tokens[1],
            blocks=blocks,
        )
        token0_task = asyncio.create_task(token0_coroutine)
        token1_task = asyncio.create_task(token1_coroutine)

        result = await asyncio.gather(token0_task, token1_task)
        return list(list(item) for item in zip(*result))

    else:
        return await balances_task

