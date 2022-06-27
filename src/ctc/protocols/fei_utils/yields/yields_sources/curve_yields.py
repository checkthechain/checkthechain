from __future__ import annotations

import asyncio
import typing

from ctc import spec
from ctc.protocols import curve_utils
from ctc.protocols import rari_utils
from .. import yields_spec


curve_farms = [
    {
        'name': 'FEI-3CRV',
        'symbol': 'FEI3CRV3CRV-f',
        'ctoken': '0xbfb6f7532d2db0fe4d83abb001c5c2b0842af4db',
    },
    {
        'name': 'D3',
        'symbol': 'D3-f',
        'ctoken': '0x5ca8ffe4dad9452ed880fa429dd0a08574225936',
    },
]


async def async_get_fei_yield_data(
    block_numbers: typing.Sequence[spec.BlockNumberReference],
) -> typing.Mapping[str, yields_spec.YieldSourceData]:

    tasks = []
    for curve_farm in curve_farms:
        coroutine = async_get_curve_farm_yield_data(
            block_numbers=block_numbers,
            ctoken=curve_farm['ctoken'],
            name=curve_farm['name'],
        )
        task = asyncio.create_task(coroutine)
        tasks.append(task)

    yield_datas = await asyncio.gather(*tasks)

    return {yield_data['name']: yield_data for yield_data in yield_datas}


async def async_get_curve_farm_yield_data(
    block_numbers: typing.Sequence[spec.BlockNumberReference],
    name: str,
    *,
    ctoken: spec.Address,
) -> yields_spec.YieldSourceData:

    underlying = await rari_utils.async_get_ctoken_underlying(ctoken)
    pool_addresses_coroutine = curve_utils.async_get_pool_tokens(underlying)
    pool_addresses_task = asyncio.create_task(pool_addresses_coroutine)

    tvl_history_coroutine = async_get_rari_farm_tvl_history(
        ctoken=ctoken,
        block_numbers=block_numbers,
    )
    tvl_history_task = asyncio.create_task(tvl_history_coroutine)

    current_yield_task = asyncio.create_task(
        async_get_fei_current_yield(ctoken)
    )
    yield_history_task = asyncio.create_task(
        async_get_fei_yield_history(block_numbers=block_numbers, ctoken=ctoken)
    )

    return {
        # metadata
        'name': 'Curve ' + name + ' Staking',
        'category': 'DEX',
        'platform': 'Curve',
        'url': 'https://app.rari.capital/fuse/pool/8',
        'staked_tokens': (await pool_addresses_task),
        'reward_tokens': [yields_spec.TRIBE],
        #
        # metrics
        'tvl_history': (await tvl_history_task),
        'tvl_history_units': 'USD',
        'current_yield': (await current_yield_task),
        'current_yield_units': {'Spot': 'APR'},
        'yield_history': (await yield_history_task),
        'yield_history_units': {'Staking': 'APR'},
    }


async def async_get_rari_farm_tvl_history(
    ctoken: spec.Address,
    block_numbers: typing.Sequence[spec.BlockNumberReference],
) -> list[float]:
    coroutines = [
        rari_utils.async_get_ctoken_tvl_and_tvb(
            ctoken=ctoken,
            block=block,
        )
        for block in block_numbers
    ]
    tvl_history = await asyncio.gather(*coroutines)
    return [item['tvl'] for item in tvl_history]


async def async_get_fei_current_yield(ctoken: spec.Address) -> dict[str, float]:
    return {
        'Spot': 0.01,
    }


async def async_get_fei_yield_history(
    block_numbers: typing.Sequence[spec.BlockNumberReference],
    ctoken: spec.Address,
) -> dict[str, list[float]]:
    return {'Staking': [0.01 for block in block_numbers]}
