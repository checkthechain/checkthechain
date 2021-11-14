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


def get_v2_pool_swaps(pool_address, start_block=None, end_block=None):

    return evm.get_events(
        event_name='Swap',
        contract_address=pool_address,
        start_block=start_block,
        end_block=end_block,
    )


def get_v2_pool_mints(pool_address, start_block=None, end_block=None):

    return evm.get_events(
        event_name='Mint',
        contract_address=pool_address,
        start_block=start_block,
        end_block=end_block,
    )


def get_v2_pool_burns(pool_address, start_block=None, end_block=None):

    return evm.get_events(
        event_name='Burn',
        contract_address=pool_address,
        start_block=start_block,
        end_block=end_block,
    )

