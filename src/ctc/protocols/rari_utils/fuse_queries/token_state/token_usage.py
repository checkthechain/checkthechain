from __future__ import annotations

from ctc import rpc
from ctc import spec
from ctc.protocols import chainlink_utils

from ... import rari_abis
from . import token_price


async def async_get_total_borrowed(
    ctoken: spec.Address,
    block: spec.BlockNumberReference = 'latest',
) -> int:
    result = await rpc.async_eth_call(
        to_address=ctoken,
        block_number=block,
        function_abi=rari_abis.ctoken_function_abis['totalBorrows'],
        empty_token=0,
    )
    if not isinstance(result, int):
        raise Exception('invalid rpc result')
    return result


async def async_get_total_liquidity(
    ctoken: spec.Address,
    block: spec.BlockNumberReference = 'latest',
) -> int:
    result = await rpc.async_eth_call(
        to_address=ctoken,
        block_number=block,
        function_abi=rari_abis.ctoken_function_abis['getCash'],
        empty_token=0,
    )
    if not isinstance(result, int):
        raise Exception('invalid rpc result')
    return result


async def async_get_reserves(
    ctoken: spec.Address,
    block: spec.BlockNumberReference = 'latest',
) -> int:
    result = await rpc.async_eth_call(
        to_address=ctoken,
        block_number=block,
        function_abi=rari_abis.ctoken_function_abis['totalReserves'],
    )
    if not isinstance(result, int):
        raise Exception('invalid rpc result')
    return result


async def async_get_ctoken_utilization(
    ctoken: spec.Address,
    block: spec.BlockNumberReference = 'latest',
) -> float:
    borrowed_coroutine = async_get_total_borrowed(ctoken, block)
    liquidity_coroutine = async_get_total_liquidity(ctoken, block)

    borrowed = await borrowed_coroutine
    liquidity = await liquidity_coroutine

    total = borrowed + liquidity

    if total == 0:
        return 0
    else:
        return borrowed / total


async def async_get_ctoken_tvl_and_tvb(
    ctoken: spec.Address,
    *,
    oracle: spec.Address | None = None,
    eth_price: spec.Number | None = None,
    block: spec.BlockNumberReference = 'latest',
    in_usd: bool = True,
) -> dict[str, spec.Number]:
    """combined into one function because tvl requires both to compute anyway"""
    import asyncio

    if not in_usd:
        borrowed_coroutine = asyncio.create_task(
            async_get_total_borrowed(ctoken=ctoken, block=block)
        )
        liquidity_coroutine = asyncio.create_task(
            async_get_total_liquidity(ctoken=ctoken, block=block)
        )

        borrowed = (await borrowed_coroutine) / 1e18
        liquidity = (await liquidity_coroutine) / 1e18

        return {'tvb': borrowed, 'tvl': borrowed + liquidity}

    else:

        if oracle is None:
            oracle = await token_price._async_get_ctoken_oracle(ctoken)

        if eth_price is None:
            eth_price = await chainlink_utils.async_get_eth_price(block=block)

        # send queries
        borrowed_coroutine = asyncio.create_task(
            async_get_total_borrowed(ctoken=ctoken, block=block)
        )
        liquidity_coroutine = asyncio.create_task(
            async_get_total_liquidity(ctoken=ctoken, block=block)
        )
        price_coroutine = asyncio.create_task(
            token_price.async_get_ctoken_price(
                ctoken=ctoken, oracle=oracle, block=block
            )
        )

        # receive results
        borrowed = (await borrowed_coroutine) / 1e18
        liquidity = (await liquidity_coroutine) / 1e18
        price = await price_coroutine

        # compute output
        return {
            'tvb': borrowed * price * eth_price,
            'tvl': (borrowed + liquidity) * price * eth_price,
        }
