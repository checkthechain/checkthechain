import asyncio
import typing

from ctc import evm
from ctc import rpc
from ctc import spec
from .. import yields_spec


cFEI = '0x7713dd9ca933848f6819f38b8352d9a15ea73f67'


async def async_get_fei_yield_data(
    block_numbers: typing.Sequence[spec.BlockNumberReference],
) -> typing.Mapping[str, yields_spec.YieldSourceData]:

    tvl_history_task = asyncio.create_task(
        async_get_compound_fei_tvl_history(block_numbers)
    )
    current_yield_task = asyncio.create_task(
        async_get_compound_fei_current_yield(block_numbers)
    )
    yield_history_task = asyncio.create_task(
        async_get_compound_fei_yield_history(block_numbers)
    )

    tvl_history = await tvl_history_task
    current_yield = await current_yield_task
    yield_history = await yield_history_task

    aave_v2: yields_spec.YieldSourceData = {
        'name': 'Compound Lending',
        'category': 'Lending',
        'platform': 'Compound',
        'staked_tokens': [yields_spec.FEI],
        'reward_tokens': [yields_spec.FEI],
        'tvl_history': tvl_history,
        'tvl_history_units': 'FEI',
        'current_yield': current_yield,
        'current_yield_units': {'Spot': 'APY', '7D': 'APY', '30D': 'APY'},
        'yield_history': yield_history,
        'yield_history_units': {'Lending Interest': 'APY'},
    }

    return {aave_v2['name']: aave_v2}


async def async_get_compound_fei_tvl_history(block_numbers) -> list[float]:

    import numpy as np

    cFEI_total_supply = await evm.async_get_erc20_total_supply_by_block(
        token=cFEI,
        blocks=block_numbers,
    )
    cFEI_total_supply = np.array(cFEI_total_supply)

    cFEI_conversions = await rpc.async_batch_eth_call(
        to_address=cFEI,
        block_numbers=block_numbers,
        function_name='exchangeRateStored',
    )
    cFEI_conversions = np.array(cFEI_conversions)

    tvl_history = cFEI_total_supply * cFEI_conversions / 1e10 / 1e18

    return list(tvl_history)


async def async_get_compound_fei_current_yield(block_numbers) -> list[float]:
    return {
        'Spot': 0.01,
        '7D': 0.99,
        '30D': 0.99,
    }


async def async_get_compound_fei_yield_history(block_numbers) -> list[float]:
    return {'Lending Interest': [0.01 for block in block_numbers]}

