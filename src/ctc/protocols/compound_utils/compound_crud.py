# see https://compound.finance/docs

from ctc import rpc

blocks_per_day = 6570
days_per_year = 365


async def async_get_supply_apy(ctoken, block=None):
    supply_rate_per_block = await rpc.async_eth_call(
        to_address=ctoken,
        function_name='supplyRatePerBlock',
        block=block,
    )
    supply_apy = (1 + supply_rate_per_block / 1e18 * blocks_per_day) ** 365 - 1
    return supply_apy


async def async_get_borrow_apy(ctoken, block=None):
    borrow_rate_per_block = await rpc.async_eth_call(
        to_address=ctoken,
        function_name='borrowRatePerBlock',
        block=block,
    )
    borrow_apy = (1 + borrow_rate_per_block / 1e18 * blocks_per_day) ** 365 - 1
    return borrow_apy


async def async_get_supply_apy_by_block(ctoken, blocks):
    import numpy as np

    supply_rate_per_block = await rpc.async_batch_eth_call(
        to_address=ctoken,
        function_name='supplyRatePerBlock',
        block_numbers=blocks,
    )
    supply_rate_per_block = np.array(supply_rate_per_block)
    supply_apy = (1 + supply_rate_per_block / 1e18 * blocks_per_day) ** 365 - 1
    return list(supply_apy)


async def async_get_borrow_apy_by_block(ctoken, blocks):
    import numpy as np

    borrow_rate_per_block = await rpc.async_batch_eth_call(
        to_address=ctoken,
        function_name='borrowRatePerBlock',
        block_numbers=blocks,
    )
    borrow_rate_per_block = np.array(borrow_rate_per_block)
    borrow_apy = (1 + borrow_rate_per_block / 1e18 * blocks_per_day) ** 365 - 1
    return list(borrow_apy)

