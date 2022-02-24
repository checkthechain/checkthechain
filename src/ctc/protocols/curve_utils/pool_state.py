from ctc import evm
from ctc import rpc

from . import pool_metadata


async def async_get_virtual_price(pool, provider=None):
    return await rpc.async_eth_call(
        to_adress=pool,
        function_name='get_virtual_price',
        function_parameters=[],
        provider=provider,
    )


async def async_get_lp_withdrawal(
    pool, amount_lp, token_withdrawn, provider=None
):

    token_index = await pool_metadata.async_get_token_index(
        pool=pool,
        token=token_withdrawn,
        provider=provider,
    )

    return await rpc.async_eth_call(
        to_address=pool,
        function_name='calc_withdraw_one_coin',
        function_parameters=[amount_lp, token_index],
        provider=provider,
    )


async def async_get_pool_state(pool, n_tokens=None, block=None, provider=None):

    total_supply = await evm.async_get_erc20_total_supply(
        token=pool,
        block=block,
        provider=provider,
    )
    token_addresses = await pool_metadata.async_get_pool_addresses(
        pool,
        n_tokens=n_tokens,
        provider=provider,
    )
    token_balances = await evm.async_get_erc20s_balance_of(
        address=pool,
        tokens=token_addresses,
        block=block,
        provider=provider,
    )

    return {
        'lp_total_supply': total_supply,
        'token_balances': token_balances,
    }

