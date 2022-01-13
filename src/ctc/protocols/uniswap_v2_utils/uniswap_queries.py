from ctc import evm


async def async_get_uni_v2_pool_state(
    pool_address,
    x_address,
    y_address,
    x_name,
    y_name,
    x_price=None,
    y_price=None,
    block=None,
    normalize=True,
):

    # balances
    x_balance = evm.async_get_erc20_balance_of(
        token=x_address,
        address=pool_address,
        block=block,
        normalize=normalize,
    )
    y_balance = evm.async_get_erc20_balance_of(
        token=y_address,
        address=pool_address,
        block=block,
        normalize=normalize,
    )
    lp_tokens = evm.async_get_erc20_total_supply(
        pool_address, block=block, normalize=normalize
    )

    state = {
        x_name + '_balance': x_balance,
        y_name + '_balance': y_balance,
        'lp_tokens': lp_tokens,
    }

    # tvl
    if x_price is not None:
        x_tvl = x_balance * x_price
        state[x_name + '_tvl'] = x_tvl
    if y_price is not None:
        y_tvl = y_balance * y_price
        state[y_name + '_tvl'] = y_tvl
    if x_price is not None and x_price is not None:
        state['tvl'] = x_tvl + y_tvl

    # number of trades
    pass

    return state


def fetch_swaps(
    address,
    x_decimals,
    y_decimals,
    start_block=None,
    end_block='latest',
    abi=None,
    parallel_kwargs={'n_workers': 60},
    blocks_per_chunk=2000,
    add_from_address=True,
):

    raise NotImplementedError()

    # if abi is None:
    #     abi = code.fetch_abi(address)

    # # fetch events
    # swaps = web3_utils.fetch_events_as_chunks(
    #     contract_address=address,
    #     contract_name=None,
    #     contract_abi=abi,
    #     event_name='Swap',
    #     start_block=start_block,
    #     end_block=end_block,
    #     blocks_per_chunk=blocks_per_chunk,
    #     parallel_kwargs=parallel_kwargs,
    # )

    # # rescale
    # swaps['arg__amount0In'] /= 10 ** x_decimals
    # swaps['arg__amount0Out'] /= 10 ** x_decimals
    # swaps['arg__amount1In'] /= 10 ** y_decimals
    # swaps['arg__amount1Out'] /= 10 ** y_decimals

    # # compute price
    # sell_mask = swaps['arg__amount0In'] != 0
    # buy_mask = swaps['arg__amount1In'] != 0
    # swaps['sell_price'] = (
    #     swaps[sell_mask]['arg__amount1Out'] / swaps[sell_mask]['arg__amount0In']
    # )
    # swaps['buy_price'] = (
    #     swaps[buy_mask]['arg__amount1In'] / swaps[buy_mask]['arg__amount0Out']
    # )
    # swaps['price'] = swaps['sell_price'].add(swaps['buy_price'], fill_value=0)

    # # add from_address
    # if add_from_address:
    #     transaction_hashes = list(set(swaps['transaction_hash'].values))
    #     transactions = web3_utils.fetch_transaction(
    #         transaction_hashes=transaction_hashes,
    #         parallel_kwargs=parallel_kwargs,
    #     )
    #     hash_to_transaction = dict(zip(transaction_hashes, transactions))
    #     from_addresses = []
    #     for transaction_hash in swaps['transaction_hash'].values:
    #         from_address = hash_to_transaction[transaction_hash]['from']
    #         from_addresses.append(from_address)
    #     swaps['from_address'] = from_addresses

    # return swaps

