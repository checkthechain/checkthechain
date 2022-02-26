import typing

from ctc import evm
from ctc import rpc
from ctc import spec

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


async def async_get_trade(
    pool: spec.Address,
    token_in: typing.Union[int, spec.Address],
    token_out: typing.Union[int, spec.Address],
    amount_in: typing.Union[int, float],
    input_normalized: bool = True,
    normalize_output: bool = True,
    provider: spec.ProviderSpec = None,
    block: typing.Optional[spec.BlockNumberReference] = None,
) -> typing.Union[int, float]:

    # get metadata
    metadata = await pool_metadata.async_get_pool_metadata(
        pool=pool,
        provider=provider,
    )
    in_index = await pool_metadata.async_get_token_index(
        pool=pool,
        token=token_in,
        metadata=metadata,
    )
    out_index = await pool_metadata.async_get_token_index(
        pool=pool,
        token=token_out,
        metadata=metadata,
    )

    # denormalize input
    if input_normalized:
        amount_in *= 10 ** metadata['token_decimals'][in_index]

    # query data
    amount_out = await rpc.async_eth_call(
        to_address=pool,
        function_name='get_dy',
        function_parameters=[
            in_index,
            out_index,
            amount_in,
        ],
        provider=provider,
        block_number=block,
    )

    # normalize output
    if normalize_output:
        amount_out = amount_out / (10 ** metadata['token_decimals'][out_index])

    return amount_out

