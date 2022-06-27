from __future__ import annotations

import typing

from ctc import rpc
from ctc import spec

from .. import irm_metadata
from .. import token_metadata
from ... import rari_abis


async def async_get_supply_interest_by_block(
    ctoken: spec.Address,
    *,
    block: spec.BlockNumberReference = 'latest',
    normalize: bool = True,
    fill_empty: bool = False,
    empty_token: typing.Any = None,
) -> int | float | None:
    result = await rpc.async_eth_call(
        to_address=ctoken,
        block_number=block,
        function_abi=rari_abis.ctoken_function_abis['supplyRatePerBlock'],
        fill_empty=fill_empty,
        empty_token=empty_token,
    )
    if fill_empty and result is None:
        return None
    if normalize:
        result /= 1e18
    return result


async def async_get_borrow_interest_by_block(
    ctoken: spec.Address,
    *,
    block: spec.BlockNumberReference = 'latest',
    normalize: bool = True,
    fill_empty: bool = False,
    empty_token: typing.Any = None,
) -> int | float | None:
    result = await rpc.async_eth_call(
        to_address=ctoken,
        block_number=block,
        function_abi=rari_abis.ctoken_function_abis['borrowRatePerBlock'],
        fill_empty=fill_empty,
        empty_token=empty_token,
    )
    if fill_empty and result is None:
        return None
    if normalize:
        result /= 1e18
    return result


async def async_get_supply_apy(
    ctoken: spec.Address,
    *,
    blocks_per_year: int | None = None,
    block: spec.BlockNumberReference = 'latest',
    fill_empty: bool = False,
    empty_token: typing.Any = None,
) -> float | None:
    supply_interest_per_block = await async_get_supply_interest_by_block(
        ctoken=ctoken,
        block=block,
        normalize=True,
        fill_empty=fill_empty,
        empty_token=empty_token,
    )
    if supply_interest_per_block is None:
        if fill_empty:
            return None
        else:
            raise Exception('could not determine supply interest per block')
    if blocks_per_year is None:
        irm = await token_metadata.async_get_ctoken_irm(ctoken, block=block)
        blocks_per_year = await irm_metadata.async_get_irm_blocks_per_year(
            irm,
            block=block,
        )

    return (1 + supply_interest_per_block) ** blocks_per_year - 1


async def async_get_borrow_apy(
    ctoken: spec.Address,
    *,
    blocks_per_year: int | None = None,
    block: spec.BlockNumberReference = 'latest',
    fill_empty: bool = False,
    empty_token: typing.Any = None,
) -> float | None:

    borrow_interest_per_block = await async_get_borrow_interest_by_block(
        ctoken=ctoken,
        block=block,
        normalize=True,
        fill_empty=fill_empty,
        empty_token=empty_token,
    )
    if borrow_interest_per_block is None:
        if fill_empty:
            return None
        else:
            raise Exception('could not determine supply interest per block')

    if blocks_per_year is None:
        irm = await token_metadata.async_get_ctoken_irm(ctoken, block=block)
        blocks_per_year = await irm_metadata.async_get_irm_blocks_per_year(
            irm,
            block=block,
        )

    return (1 + borrow_interest_per_block) ** blocks_per_year - 1
