from __future__ import annotations

import asyncio
import typing

from typing_extensions import TypedDict

from ctc import spec
from ctc.toolbox import nested_utils
from . import directory_metadata
from . import pool_metadata
from . import token_metadata
from . import token_state


class CTokenMetricSpec(TypedDict, total=False):
    tvl: bool
    tvb: bool
    supply_apy: bool
    borrow_apy: bool


class CTokenMetrics(TypedDict, total=False):
    tvl: float
    tvb: float
    supply_apy: float
    borrow_apy: float


class CTokenMetricsByBlock(TypedDict, total=False):
    tvl: typing.Sequence[float]
    tvb: typing.Sequence[float]
    supply_apy: typing.Sequence[float]
    borrow_apy: typing.Sequence[float]


async def async_get_token_multipool_history(
    token, blocks, metrics=None, comptrollers=None
):
    """get token metrics across multiple pools and blocks"""

    if comptrollers is None:
        pools = await directory_metadata.async_get_all_pools()
        comptrollers = [pool[2] for pool in pools]

    coroutines = []
    for comptroller in comptrollers:
        coroutine = async_get_pool_token_history(
            comptroller, token, blocks, metrics=metrics
        )
        coroutines.append(coroutine)
    results = await asyncio.gather(*coroutines)

    return {
        comptroller: result
        for comptroller, result in zip(comptrollers, results)
        if result is not None
    }


async def async_get_pool_token_history(
    comptroller, token, blocks, metrics=None
):
    """get metrics of a token in a pool across blocks"""
    ctokens = await pool_metadata.async_get_pool_ctokens(comptroller)
    coroutines = []
    for ctoken in ctokens:
        coroutine = _async_get_token_history_if_match(
            ctoken, token, blocks, metrics=metrics
        )
        coroutines.append(coroutine)
    results = await asyncio.gather(*coroutines)

    matching_results = [result for result in results if result is not None]

    if len(matching_results) == 0:
        return None
    elif len(matching_results) == 1:
        return matching_results[0]
    else:
        raise Exception('more than one ctoken found for underlying')


async def _async_get_token_history_if_match(
    ctoken, token, blocks, metrics=None
):
    underlying = await token_metadata.async_get_ctoken_underlying(ctoken)
    if underlying != token.lower():
        return None
    else:
        return await async_get_ctoken_state_by_block(
            ctoken=ctoken,
            blocks=blocks,
            metrics=metrics,
            in_usd=False,
        )


async def async_get_ctoken_state_by_block(
    ctoken,
    blocks,
    metrics=None,
    eth_price=None,
    in_usd=True,
):
    coroutines = []
    for block in blocks:
        coroutine = async_get_ctoken_state(
            ctoken,
            block=block,
            metrics=metrics,
            eth_price=eth_price,
            in_usd=in_usd,
        )
        coroutines.append(coroutine)
    results = await asyncio.gather(*coroutines)
    return nested_utils.list_of_dicts_to_dict_of_lists(results)


async def async_get_ctoken_state(
    ctoken: spec.Address,
    block: spec.BlockNumberReference = 'latest',
    metrics: CTokenMetricSpec = None,
    eth_price: typing.SupportsFloat | None = None,
    in_usd: bool = True,
):
    if metrics is None:
        metrics = {
            'tvl': True,
            'tvb': True,
            'supply_apy': True,
            'borrow_apy': True,
        }

    blocks_per_year = 2102400
    if metrics.get('tvl') or metrics.get('tvb'):
        coroutine = token_state.async_get_ctoken_tvl_and_tvb(
            ctoken=ctoken,
            block=block,
            in_usd=in_usd,
            eth_price=eth_price,
        )
        tv_task = asyncio.create_task(coroutine)
    if metrics.get('supply_apy'):
        coroutine = token_state.async_get_supply_apy(
            ctoken=ctoken,
            block=block,
            blocks_per_year=blocks_per_year,
            fill_empty=True,
            empty_token=0,
        )
        supply_task = asyncio.create_task(coroutine)
    if metrics.get('borrow_apy'):
        coroutine = token_state.async_get_borrow_apy(
            ctoken=ctoken,
            block=block,
            blocks_per_year=blocks_per_year,
            fill_empty=True,
            empty_token=0,
        )
        borrow_task = asyncio.create_task(coroutine)

    # gather output
    output: CTokenMetrics = {}
    if metrics.get('tvl') or metrics.get('tvb'):
        tv_result = await tv_task
        if metrics.get('tvl'):
            output['tvl'] = tv_result['tvl']
        if metrics.get('tvb'):
            output['tvb'] = tv_result['tvb']
    if metrics.get('supply_apy'):
        output['supply_apy'] = await supply_task
    if metrics.get('borrow_apy'):
        output['borrow_apy'] = await borrow_task

    return output

