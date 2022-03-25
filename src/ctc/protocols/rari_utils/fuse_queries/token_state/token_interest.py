from __future__ import annotations

from ctc import rpc
from .. import irm_metadata
from .. import token_metadata
from ... import rari_abis


async def async_get_supply_interest_per_block(
    ctoken,
    block='latest',
    normalize=True,
    fill_empty=False,
    empty_token=None,
):
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


async def async_get_borrow_interest_per_block(
    ctoken,
    block='latest',
    normalize=True,
    fill_empty=False,
    empty_token=None,
):
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
    ctoken,
    blocks_per_year=None,
    block='latest',
    fill_empty=False,
    empty_token=None,
):
    supply_interest_per_block = await async_get_supply_interest_per_block(
        ctoken=ctoken,
        block=block,
        normalize=True,
        fill_empty=fill_empty,
        empty_token=empty_token,
    )
    if fill_empty and supply_interest_per_block is None:
        return None
    if blocks_per_year is None:
        irm = await token_metadata.async_get_ctoken_irm(ctoken, block=block)
        blocks_per_year = await irm_metadata.async_get_irm_blocks_per_year(
            irm,
            block=block,
        )

    return (1 + supply_interest_per_block) ** blocks_per_year - 1


async def async_get_borrow_apy(
    ctoken,
    blocks_per_year=None,
    block='latest',
    fill_empty=False,
    empty_token=None,
):

    borrow_interest_per_block = await async_get_borrow_interest_per_block(
        ctoken=ctoken,
        block=block,
        normalize=True,
        fill_empty=fill_empty,
        empty_token=empty_token,
    )
    if fill_empty and borrow_interest_per_block is None:
        return None

    if blocks_per_year is None:
        irm = await token_metadata.async_get_ctoken_irm(ctoken, block=block)
        blocks_per_year = await irm_metadata.async_get_irm_blocks_per_year(
            irm,
            block=block,
        )

    return (1 + borrow_interest_per_block) ** blocks_per_year - 1

