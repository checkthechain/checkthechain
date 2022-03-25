"""
see https://docs.aave.com/developers/v/2.0/guides/apy-and-apr

incentives not currently included
"""

import asyncio

from ctc import rpc
from ctc.toolbox import nested_utils


ray = 10 ** 27
seconds_per_year = 31536000

aave_lending_pool = '0x7d2768de32b0b80b7a3454c06bdac94a69ddc7a9'


async def async_get_reserve_data(asset, block=None):

    keys = [
        'configuration',
        'liquidity_index',
        'variable_borrow_index',
        'current_liquidity_rate',
        'current_variable_borrow_rate',
        'current_stable_borrow_rate',
        'last_update_timestamp',
        'atoken_address',
        'stable_debt_token_address',
        'varaible_debt_token_address',
        'interest_rate_strategy_address',
        'id',
    ]

    result = await rpc.async_eth_call(
        to_address=aave_lending_pool,
        function_name='getReserveData',
        function_parameters=[asset],
        block_number=block,
    )

    return dict(zip(keys, result))


async def async_get_reserve_data_by_block(asset, blocks):

    coroutines = [
        async_get_reserve_data(asset, block=block) for block in blocks
    ]

    results = await asyncio.gather(*coroutines)
    return nested_utils.list_of_dicts_to_dict_of_lists(results)


async def async_get_interest_rates(token, block=None):
    reserve_data = await async_get_reserve_data(asset=token, block=block)

    supply_apr = reserve_data['current_liquidity_rate'] / ray
    supply_apy = (1 + supply_apr / seconds_per_year) ** seconds_per_year - 1
    borrow_apr = reserve_data['current_variable_borrow_rate'] / ray
    borrow_apy = (1 + borrow_apr / seconds_per_year) ** seconds_per_year - 1

    return {
        'supply_apr': list(supply_apr),
        'supply_apy': list(supply_apy),
        'borrow_apr': list(borrow_apr),
        'borrow_apy': list(borrow_apy),
    }


async def async_get_interest_rates_by_block(token, blocks=None):
    import numpy as np

    reserve_data = await async_get_reserve_data_by_block(
        asset=token, blocks=blocks
    )

    currrent_liquidity_rate = np.array(reserve_data['current_liquidity_rate'])
    current_variable_borrow_rate = np.array(
        reserve_data['current_variable_borrow_rate']
    )

    supply_apr = currrent_liquidity_rate / ray
    supply_apy = (1 + supply_apr / seconds_per_year) ** seconds_per_year - 1
    borrow_apr = current_variable_borrow_rate / ray
    borrow_apy = (1 + borrow_apr / seconds_per_year) ** seconds_per_year - 1

    return {
        'supply_apr': list(supply_apr),
        'supply_apy': list(supply_apy),
        'borrow_apr': list(borrow_apr),
        'borrow_apy': list(borrow_apy),
    }

