"""
see https://docs.aave.com/developers/v/2.0/guides/apy-and-apr

incentives not currently included
"""
from __future__ import annotations

import asyncio
import typing
from typing_extensions import TypedDict

from ctc import rpc
from ctc import spec
from ctc.toolbox import nested_utils


ray = 10 ** 27
seconds_per_year = 31536000

aave_lending_pool = '0x7d2768de32b0b80b7a3454c06bdac94a69ddc7a9'


class AaveV2ReserveData(TypedDict):
    configuration: int
    liquidity_index: int
    variable_borrow_index: int
    current_liquidity_rate: int
    current_variable_borrow_rate: int
    current_stable_borrow_rate: int
    last_update_timestamp: int
    atoken_address: spec.Address
    stable_debt_token_address: spec.Address
    variable_debt_token_address: spec.Address
    interest_rate_strategy_address: spec.Address
    id: int


class AaveV2ReserveListData(TypedDict):
    configuration: list[int]
    liquidity_index: list[int]
    variable_borrow_index: list[int]
    current_liquidity_rate: list[int]
    current_variable_borrow_rate: list[int]
    current_stable_borrow_rate: list[int]
    last_update_timestamp: list[int]
    atoken_address: list[spec.Address]
    stable_debt_token_address: list[spec.Address]
    variable_debt_token_address: list[spec.Address]
    interest_rate_strategy_address: list[spec.Address]
    id: list[int]


async def async_get_reserve_data(
    asset: spec.Address,
    block: spec.BlockNumberReference | None = None,
) -> AaveV2ReserveData:

    result = await rpc.async_eth_call(
        to_address=aave_lending_pool,
        function_name='getReserveData',
        function_parameters=[asset],
        block_number=block,
    )

    return {
        'configuration': result[0],
        'liquidity_index': result[1],
        'variable_borrow_index': result[2],
        'current_liquidity_rate': result[3],
        'current_variable_borrow_rate': result[4],
        'current_stable_borrow_rate': result[5],
        'last_update_timestamp': result[6],
        'atoken_address': result[7],
        'stable_debt_token_address': result[8],
        'variable_debt_token_address': result[9],
        'interest_rate_strategy_address': result[10],
        'id': result[11],
    }


async def async_get_reserve_data_by_block(
    asset: spec.Address, blocks: typing.Sequence[spec.BlockNumberReference]
) -> AaveV2ReserveListData:

    coroutines = [
        async_get_reserve_data(asset, block=block) for block in blocks
    ]

    results = await asyncio.gather(*coroutines)
    return typing.cast(
        AaveV2ReserveListData,
        nested_utils.list_of_dicts_to_dict_of_lists(results),
    )


async def async_get_interest_rates(
    token: spec.Address,
    block: spec.BlockNumberReference | None = None,
) -> dict[str, float]:
    reserve_data = await async_get_reserve_data(asset=token, block=block)

    supply_apr = reserve_data['current_liquidity_rate'] / ray
    supply_apy = (1 + supply_apr / seconds_per_year) ** seconds_per_year - 1
    borrow_apr = reserve_data['current_variable_borrow_rate'] / ray
    borrow_apy = (1 + borrow_apr / seconds_per_year) ** seconds_per_year - 1

    return {
        'supply_apr': supply_apr,
        'supply_apy': supply_apy,
        'borrow_apr': borrow_apr,
        'borrow_apy': borrow_apy,
    }


async def async_get_interest_rates_by_block(
    token: spec.Address,
    blocks: typing.Sequence[spec.BlockNumberReference],
) -> dict[str, list[float]]:
    import numpy as np

    reserve_data = await async_get_reserve_data_by_block(
        asset=token, blocks=blocks
    )

    currrent_liquidity_rate: spec.NumpyArray = np.array(
        reserve_data['current_liquidity_rate']
    )
    current_variable_borrow_rate: spec.NumpyArray = np.array(
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
