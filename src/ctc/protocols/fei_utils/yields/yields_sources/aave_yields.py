from __future__ import annotations

import asyncio
import typing

from ctc import evm
from ctc import spec
from ctc.protocols import aave_v2_utils
from .. import yields_spec


aFEI = '0x683923db55fead99a79fa01a27eec3cb19679cc3'


async def async_get_fei_yield_data(
    block_numbers: typing.Sequence[spec.BlockNumberReference],
) -> typing.Mapping[str, yields_spec.YieldSourceData]:

    tvl_history_task = asyncio.create_task(
        async_get_aave_fei_tvl_history(block_numbers)
    )
    yield_history_task = asyncio.create_task(
        async_get_aave_fei_yield_history(block_numbers)
    )

    tvl_history = await tvl_history_task
    yield_history = await yield_history_task
    current_yield = {'Spot': yield_history['Lending Interest'][-1]}

    aave_v2: yields_spec.YieldSourceData = {
        'name': 'Aave Lending',
        'category': 'Lending',
        'platform': 'Aave',
        'url': 'https://app.aave.com/',
        'staked_tokens': [yields_spec.FEI],
        'reward_tokens': [yields_spec.FEI],
        'tvl_history': tvl_history,
        'tvl_history_units': 'FEI',
        'current_yield': current_yield,
        'current_yield_units': {'Spot': 'APY'},
        'yield_history': yield_history,
        'yield_history_units': {'Lending Interest': 'APY'},
    }

    return {aave_v2['name']: aave_v2}


async def async_get_aave_fei_tvl_history(
    block_numbers: typing.Sequence[spec.BlockNumberReference],
) -> list[float]:
    tvls = await evm.async_get_erc20_total_supply_by_block(
        token=aFEI,
        blocks=block_numbers,
    )
    return [float(tvl) for tvl in tvls]


async def async_get_aave_fei_yield_history(
    block_numbers: typing.Sequence[spec.BlockNumberReference],
) -> dict[str, list[float]]:
    interest_rates = await aave_v2_utils.async_get_interest_rates_by_block(
        token=yields_spec.FEI,
        blocks=block_numbers,
    )
    return {'Lending Interest': list(interest_rates['supply_apy'])}
