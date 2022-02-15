import asyncio

from ctc import rpc
from ctc.protocols import chainlink_utils

from .. import rari_abis
from . import irm_metadata
from . import pool_metadata
from . import token_metadata


async def async_get_ctoken_price(
    ctoken, oracle=None, block='latest', normalize=True
):

    if oracle is None:
        oracle = await _async_get_ctoken_oracle(ctoken=ctoken)

    price = await rpc.async_eth_call(
        to_address=oracle,
        block_number=block,
        function_abi=rari_abis.oracle_abis['getUnderlyingPrice'],
        function_parameters=[ctoken],
    )
    if normalize:
        price /= 1e18
    return price


async def async_get_total_borrowed(ctoken, block='latest'):
    return await rpc.async_eth_call(
        to_address=ctoken,
        block_number=block,
        function_abi=rari_abis.ctoken_function_abis['totalBorrows'],
        empty_token=0,
    )


async def async_get_total_liquidity(ctoken, block='latest'):
    return await rpc.async_eth_call(
        to_address=ctoken,
        block_number=block,
        function_abi=rari_abis.ctoken_function_abis['getCash'],
        empty_token=0,
    )


async def async_get_reserves(ctoken, block='latest'):
    return await rpc.async_eth_call(
        to_address=ctoken,
        block_number=block,
        function_abi=rari_abis.ctoken_function_abis['totalReserves'],
    )


async def async_get_ctoken_utilization(ctoken, block='latest'):
    borrowed_coroutine = async_get_total_borrowed(ctoken, block)
    liquidity_coroutine = async_get_total_liquidity(ctoken, block)

    borrowed = await borrowed_coroutine
    liquidity = await liquidity_coroutine

    total = borrowed + liquidity

    if total == 0:
        return 0
    else:
        return borrowed / total


async def async_get_ctoken_exchange_rate(ctoken, block='latest'):
    return await rpc.async_eth_call(
        to_address=ctoken,
        function_abi=rari_abis.ctoken_function_abis['exchangeRateCurrent'],
        block_number=block,
        empty_token=None,
    )


async def async_get_ctoken_exchange_rate_by_block(ctoken, blocks):
    return await rpc.async_batch_eth_call(
        to_address=ctoken,
        function_abi=rari_abis.ctoken_function_abis['exchangeRateCurrent'],
        block_numbers=blocks,
        empty_token=None,
    )


async def async_get_supply_interest_per_block(
    ctoken, block='latest', normalize=True
):
    result = await rpc.async_eth_call(
        to_address=ctoken,
        block_number=block,
        function_abi=rari_abis.ctoken_function_abis['supplyRatePerBlock'],
    )
    if normalize:
        result /= 1e18
    return result


async def async_get_borrow_interest_per_block(
    ctoken, block='latest', normalize=True
):
    result = await rpc.async_eth_call(
        to_address=ctoken,
        block_number=block,
        function_abi=rari_abis.ctoken_function_abis['borrowRatePerBlock'],
    )
    if normalize:
        result /= 1e18
    return result


async def async_get_supply_apy(ctoken, blocks_per_year=None, block='latest'):
    supply_interest_per_block = await async_get_supply_interest_per_block(
        ctoken=ctoken,
        block=block,
        normalize=True,
    )
    if blocks_per_year is None:
        irm = await token_metadata.async_get_ctoken_irm(ctoken, block=block)
        blocks_per_year = await irm_metadata.async_get_irm_blocks_per_year(
            irm,
            block=block,
        )

    return (1 + supply_interest_per_block) ** blocks_per_year - 1


async def async_get_borrow_apy(ctoken, blocks_per_year=None, block='latest'):

    borrow_interest_per_block = await async_get_borrow_interest_per_block(
        ctoken=ctoken,
        block=block,
        normalize=True,
    )

    if blocks_per_year is None:
        irm = await token_metadata.async_get_ctoken_irm(ctoken, block=block)
        blocks_per_year = await irm_metadata.async_get_irm_blocks_per_year(
            irm,
            block=block,
        )

    return (1 + borrow_interest_per_block) ** blocks_per_year - 1


async def async_get_ctoken_tvl_and_tvb(
    ctoken,
    oracle=None,
    eth_price=None,
    block='latest',
    in_usd=True,
):
    if not in_usd:
        borrowed = asyncio.create_task(
            async_get_total_borrowed(ctoken=ctoken, block=block)
        )
        liquidity = asyncio.create_task(
            async_get_total_liquidity(ctoken=ctoken, block=block)
        )

        borrowed = await borrowed
        borrowed /= 1e18
        liquidity = await liquidity
        liquidity /= 1e18

        return {'tvb': borrowed, 'tvl': borrowed + liquidity}

    if oracle is None:
        oracle = await _async_get_ctoken_oracle(ctoken)

    if eth_price is None:
        eth_price = await chainlink_utils.async_get_eth_price(block=block)

    # send queries
    borrowed = asyncio.create_task(
        async_get_total_borrowed(ctoken=ctoken, block=block)
    )
    liquidity = asyncio.create_task(
        async_get_total_liquidity(ctoken=ctoken, block=block)
    )
    price = asyncio.create_task(
        async_get_ctoken_price(ctoken=ctoken, oracle=oracle, block=block)
    )

    # receive results
    borrowed = await borrowed
    borrowed /= 1e18
    liquidity = await liquidity
    liquidity /= 1e18
    price = await price

    # compute output
    return {
        'tvb': borrowed * price * eth_price,
        'tvl': (borrowed + liquidity) * price * eth_price,
    }


async def _async_get_ctoken_oracle(ctoken):
    comptroller = await token_metadata.async_get_ctoken_comptroller(ctoken)
    oracle = await pool_metadata.async_get_pool_oracle(comptroller)
    return oracle

