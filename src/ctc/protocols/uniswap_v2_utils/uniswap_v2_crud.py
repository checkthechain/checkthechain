import asyncio

from ctc import evm
from ctc import rpc


#
# # metadata
#


async def async_get_pool_tokens(pool_address, **rpc_kwargs):
    kwargs = dict(rpc_kwargs, to_address=pool_address)
    return await asyncio.gather(
        rpc.async_eth_call(function_name='token0', **kwargs),
        rpc.async_eth_call(function_name='token1', **kwargs),
    )


async def async_get_pool_metadata(pool_address, **rpc_kwargs):
    x_address, y_address = await async_get_pool_tokens(
        pool_address=pool_address
    )
    x_symbol, y_symbol = await evm.async_get_erc20s_symbols(
        tokens=[x_address, y_address], **rpc_kwargs
    )
    return {
        'x_symbol': x_symbol,
        'y_symbol': y_symbol,
        'x_address': x_address,
        'y_address': y_address,
    }


#
# # old sync functions
#


def get_pool_tokens(pool_address):
    token0 = evm.eth_call(to_address=pool_address, function_name='token0')
    token1 = evm.eth_call(to_address=pool_address, function_name='token1')
    return [token0, token1]


def get_pool_metadata(pool_address):
    token_x, token_y = get_pool_tokens(pool_address=pool_address)
    token_x_symbol = evm.get_erc20_symbol(token=token_x)
    token_y_symbol = evm.get_erc20_symbol(token=token_y)
    return {
        'x_symbol': token_x_symbol,
        'y_symbol': token_y_symbol,
        'x_address': token_x,
        'y_address': token_y,
    }


#
# # state
#


async def async_get_pool_state(pool_address, block='latest'):
    block = await evm.async_block_number_to_int(block)

    # reserves
    token_x, token_y = await async_get_pool_tokens(pool_address=pool_address)
    reserves_coroutine = evm.async_get_erc20s_balance_of(
        address=pool_address,
        tokens=[token_x, token_y],
        block=block,
    )
    reserves_coroutine = asyncio.create_task(reserves_coroutine)

    # total supply
    lp_total_supply_coroutine = evm.async_get_erc20_total_supply(
        token=pool_address,
        block=block,
    )
    lp_total_supply_coroutine = asyncio.create_task(lp_total_supply_coroutine)

    # await results
    token_x_reserves, token_y_reserves = await reserves_coroutine
    lp_total_supply = await lp_total_supply_coroutine

    return {
        'x_reserves': token_x_reserves,
        'y_reserves': token_y_reserves,
        'lp_total_supply': lp_total_supply,
    }


async def async_get_pool_state_by_block():
    raise NotImplementedError()


@evm.parallelize_block_fetching()
def get_pool_state(pool_address, block='latest'):

    block = evm.normalize_block(block=block)

    token_x, token_y = get_pool_tokens(pool_address=pool_address)
    token_x_reserves = evm.get_erc20_balance_of(
        pool_address, token=token_x, block=block
    )
    token_y_reserves = evm.get_erc20_balance_of(
        pool_address, token=token_y, block=block
    )
    lp_total_supply = evm.get_erc20_total_supply(
        token=pool_address, block=block
    )

    return {
        'x_reserves': token_x_reserves,
        'y_reserves': token_y_reserves,
        'lp_total_supply': lp_total_supply,
    }


# def get_v2_pool_state(pool_address, block=None, blocks=None):
#     pass


#
# # events
#


async def async_get_pool_swaps(
    pool_address,
    start_block=None,
    end_block=None,
    replace_symbols=False,
    normalize=True,
):
    if normalize or replace_symbols:
        metadata_task = asyncio.create_task(
            async_get_pool_metadata(pool_address)
        )

    swaps = evm.get_events(
        event_name='Swap',
        contract_address=pool_address,
        start_block=start_block,
        end_block=end_block,
    )

    if normalize or replace_symbols:
        metadata = await metadata_task

    # rename columns
    if replace_symbols:
        x_symbol = metadata['x_symbol']
        y_symbol = metadata['y_symbol']
    else:
        x_symbol = 'x'
        y_symbol = 'y'
    columns = {
        'arg__amount0In': x_symbol + '_sold',
        'arg__amount0Out': x_symbol + '_bought',
        'arg__amount1In': y_symbol + '_sold',
        'arg__amount1Out': y_symbol + '_bought',
    }
    swaps = swaps.rename(columns=columns)

    # normalize columns
    if normalize:
        x_decimals, y_decimals = await evm.async_get_erc20s_decimals(
            tokens=[metadata['x_address'], metadata['y_address']],
        )
        swaps[columns['arg__amount0In']] = swaps[
            columns['arg__amount0In']
        ].astype(float) / (10 ** x_decimals)
        swaps[columns['arg__amount0Out']] = swaps[
            columns['arg__amount0Out']
        ].astype(float) / (10 ** x_decimals)
        swaps[columns['arg__amount1In']] = swaps[
            columns['arg__amount1In']
        ].astype(float) / (10 ** y_decimals)
        swaps[columns['arg__amount1Out']] = swaps[
            columns['arg__amount1Out']
        ].astype(float) / (10 ** y_decimals)

    return swaps


async def async_get_pool_mints(
    pool_address,
    start_block=None,
    end_block=None,
    # replace_symbols=False,
    # normalize=True,
):
    return evm.get_events(
        event_name='Mint',
        contract_address=pool_address,
        start_block=start_block,
        end_block=end_block,
    )


async def async_get_pool_burns(
    pool_address,
    start_block=None,
    end_block=None,
    # replace_symbols=False,
    # normalize=True,
):
    return evm.get_events(
        event_name='Burn',
        contract_address=pool_address,
        start_block=start_block,
        end_block=end_block,
    )


def get_pool_swaps(pool_address, start_block=None, end_block=None):

    return evm.get_events(
        event_name='Swap',
        contract_address=pool_address,
        start_block=start_block,
        end_block=end_block,
    )


def get_pool_mints(pool_address, start_block=None, end_block=None):

    return evm.get_events(
        event_name='Mint',
        contract_address=pool_address,
        start_block=start_block,
        end_block=end_block,
    )


def get_pool_burns(pool_address, start_block=None, end_block=None):

    return evm.get_events(
        event_name='Burn',
        contract_address=pool_address,
        start_block=start_block,
        end_block=end_block,
    )

