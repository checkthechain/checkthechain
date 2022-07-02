from __future__ import annotations

import asyncio
import typing

from ctc import evm
from ctc import rpc
from ctc import spec
from ctc.protocols import compound_utils
from .. import yields_spec


cFEI = '0x7713dd9ca933848f6819f38b8352d9a15ea73f67'


async def async_get_fei_yield_data(
    block_numbers: typing.Sequence[spec.BlockNumberReference],
) -> typing.Mapping[str, yields_spec.YieldSourceData]:

    tvl_history_task = asyncio.create_task(
        async_get_compound_fei_tvl_history(block_numbers)
    )
    yield_history_task = asyncio.create_task(
        async_get_compound_fei_yield_history(block_numbers)
    )

    tvl_history = await tvl_history_task
    yield_history = await yield_history_task
    current_yield = {'Spot': yield_history['Lending Interest'][-1]}

    aave_v2: yields_spec.YieldSourceData = {
        'name': 'Compound Lending',
        'category': 'Lending',
        'platform': 'Compound',
        'url': 'https://app.compound.finance',
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


async def async_get_compound_fei_tvl_history(
    block_numbers: typing.Sequence[spec.BlockNumberReference],
) -> list[float]:

    import numpy as np

    cFEI_total_supply = await evm.async_get_erc20_total_supply_by_block(
        token=cFEI,
        blocks=block_numbers,
    )
    cFEI_total_supply_array: spec.NumpyArray = np.array(cFEI_total_supply)

    cFEI_conversions = await rpc.async_batch_eth_call(
        to_address=cFEI,
        block_numbers=block_numbers,
        function_name='exchangeRateStored',
    )
    cFEI_conversions_array: spec.NumpyArray = np.array(cFEI_conversions)

    tvl_history = cFEI_total_supply_array * cFEI_conversions_array / 1e10 / 1e18

    return list(tvl_history)


async def async_get_compound_fei_yield_history(
    block_numbers: typing.Sequence[spec.BlockNumberReference],
) -> dict[str, list[float]]:
    supply_apy = await compound_utils.async_get_supply_apy_by_block(
        cFEI,
        blocks=block_numbers,
    )
    return {'Lending Interest': supply_apy}
