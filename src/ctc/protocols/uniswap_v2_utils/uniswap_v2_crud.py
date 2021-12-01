import asyncio

from ctc import evm


#
# # metadata
#


def get_pool_tokens(pool_address):
    token0 = evm.eth_call(to_address=pool_address, function_name='token0')
    token1 = evm.eth_call(to_address=pool_address, function_name='token1')
    return [token0, token1]


def get_pool_metadata(pool_address):
    token_x, token_y = get_pool_tokens(pool_address=pool_address)
    token_x_name = evm.get_erc20_name(token=token_x)
    token_y_name = evm.get_erc20_name(token=token_y)
    return {
        'x_name': token_x_name,
        'y_name': token_y_name,
        'x_address': token_x,
        'y_address': token_y,
    }


#
# # state
#


@evm.parallelize_block_fetching()
def get_v2_pool_state(pool_address, block='latest'):

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
    pool_address, start_block=None, end_block=None, replace_names=False, normalize=True
):
    if normalize or replace_names:
        metadata_task = asyncio.create_task(async_get_pool_metadata(pool_address))

    swaps = evm.get_events(
        event_name='Swap',
        contract_address=pool_address,
        start_block=start_block,
        end_block=end_block,
    )

    if normalize or replace_names:
        metadata = await metadata_task

    # rename columns
    if replace_names:
        x_name = metadata['x_name']
        y_name = metadata['y_name']
    else:
        x_name = 'x'
        y_name = 'y'
    columns = {
        'arg__amount0In': x_name + '_sold',
        'arg__amount0Out': x_name + '_bought',
        'arg__amount1In': y_name + '_sold',
        'arg__amount1Out': y_name + '_bought',
    }
    swaps = swaps.rename(columns=columns)

    # normalize columns
    if normalize:
        x_decimals = metadata['x_address']
        y_decimals = metadata['y_address']
        await evm.async_get_erc20_decimals(
            token='0x956f47f50a910163d8bf957cf5846d573e7f87ca',
        )
        await evm.async_get_erc20_decimals(
            token='0xc7283b66eb1eb5fb86327f08e1b5816b0720212b',
        )

    return swaps


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

