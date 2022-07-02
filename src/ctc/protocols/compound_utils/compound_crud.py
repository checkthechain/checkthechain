# see https://compound.finance/docs
from __future__ import annotations

import typing

from ctc import rpc
from ctc import spec

blocks_per_day = 6570
days_per_year = 365


async def async_get_supply_apy(
    ctoken: spec.Address,
    block: spec.BlockNumberReference | None = None,
) -> float:
    result = await rpc.async_eth_call(
        to_address=ctoken,
        function_name='supplyRatePerBlock',
        block_number=block,
    )
    if not isinstance(result, int):
        raise Exception('invalid rpc result')
    supply_rate_per_block = result
    supply_apy = (1 + supply_rate_per_block / 1e18 * blocks_per_day) ** 365 - 1
    return supply_apy


async def async_get_borrow_apy(
    ctoken: spec.Address,
    block: spec.BlockNumberReference | None = None,
) -> float:
    result = await rpc.async_eth_call(
        to_address=ctoken,
        function_name='borrowRatePerBlock',
        block_number=block,
    )
    if not isinstance(result, int):
        raise Exception('invalid rpc result')
    borrow_rate_per_block = result
    borrow_apy = (1 + borrow_rate_per_block / 1e18 * blocks_per_day) ** 365 - 1
    return borrow_apy


async def async_get_supply_apy_by_block(
    ctoken: spec.Address,
    blocks: typing.Sequence[spec.BlockNumberReference],
) -> list[float]:

    import numpy as np

    supply_rate_per_block = await rpc.async_batch_eth_call(
        to_address=ctoken,
        function_name='supplyRatePerBlock',
        block_numbers=blocks,
    )
    as_array: spec.NumpyArray = np.array(supply_rate_per_block)
    supply_apy = (1 + as_array / 1e18 * blocks_per_day) ** 365 - 1
    return list(supply_apy)


async def async_get_borrow_apy_by_block(
    ctoken: spec.Address,
    blocks: typing.Sequence[spec.BlockNumberReference],
) -> list[float]:

    import numpy as np

    borrow_rate_per_block = await rpc.async_batch_eth_call(
        to_address=ctoken,
        function_name='borrowRatePerBlock',
        block_numbers=blocks,
    )
    as_array: spec.NumpyArray = np.array(borrow_rate_per_block)
    borrow_apy = (1 + as_array / 1e18 * blocks_per_day) ** 365 - 1
    return list(borrow_apy)
