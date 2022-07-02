from __future__ import annotations

import asyncio
import typing

from ctc import evm
from ctc import spec
from ctc.protocols import g_uni_utils
from .. import yields_spec


G_UNI_FEI_USDC = '0xcf84a3dc12319531e3debd48c86e68eaeaff224a'
G_UNI_FEI_DAI = '0x3d1556e84783672f2a3bd187a592520291442539'


async def async_get_fei_yield_data(
    block_numbers: typing.Sequence[spec.BlockNumberReference],
) -> typing.Mapping[str, yields_spec.YieldSourceData]:

    tasks = []
    for g_uni_pool in [
        G_UNI_FEI_USDC,
        G_UNI_FEI_DAI,
    ]:
        coroutine = async_compute_g_uni_yield_data(
            block_numbers=block_numbers, g_uni_pool=g_uni_pool
        )
        task = asyncio.create_task(coroutine)
        tasks.append(task)

    yield_datas = await asyncio.gather(*tasks)

    return {yield_data['name']: yield_data for yield_data in yield_datas}


async def async_compute_g_uni_yield_data(
    block_numbers: typing.Sequence[spec.BlockNumberReference],
    g_uni_pool: spec.Address,
) -> yields_spec.YieldSourceData:

    # compute metadata
    tokens = await g_uni_utils.async_get_tokens(g_uni_pool)
    symbols = await evm.async_get_erc20s_symbols(tokens)
    name = 'G-UNI ' + '-'.join(symbols) + ' Staking'

    # compute current_yield
    coroutine = async_get_fei_current_yield(block_numbers, g_uni_pool)
    current_yield_task = asyncio.create_task(coroutine)

    # compute yield history
    history_coroutine = async_get_fei_yield_history(block_numbers, g_uni_pool)
    yield_history_task = asyncio.create_task(history_coroutine)

    # compute tvl
    tvl_history = await async_get_fei_tvl_history(block_numbers, g_uni_pool)

    # await remaining
    yield_history = await yield_history_task
    current_yield = await current_yield_task

    return {
        'name': name,
        'category': 'DEX',
        'platform': 'Uniswap V3',
        'url': 'https://app.rari.capital/fuse/pool/8',
        'staked_tokens': list(tokens),
        'reward_tokens': [yields_spec.TRIBE],
        'tvl_history': tvl_history,
        'tvl_history_units': 'USD',
        'current_yield': current_yield,
        'current_yield_units': {'Spot': 'APR'},
        'yield_history': yield_history,
        'yield_history_units': {'Staking': 'APR'},
    }


async def async_get_fei_tvl_history(
    block_numbers: typing.Sequence[spec.BlockNumberReference],
    g_uni_pool: spec.Address,
) -> list[float]:
    balances = await g_uni_utils.async_get_token_balances_by_block(
        g_uni_pool=g_uni_pool,
        blocks=block_numbers,
    )

    # TODO: fetch asset prices instead of assuming price is static at 1
    tvl_history = [sum(block_balances) for block_balances in balances]

    return tvl_history


async def async_get_fei_current_yield(
    block_numbers: typing.Sequence[spec.BlockNumberReference],
    g_uni_pool: spec.Address,
) -> dict[str, float]:
    return {
        'Spot': 0.01,
    }


async def async_get_fei_yield_history(
    block_numbers: typing.Sequence[spec.BlockNumberReference],
    g_uni_pool: spec.Address,
) -> dict[str, list[float]]:
    return {'Staking': [0.01 for block in block_numbers]}
