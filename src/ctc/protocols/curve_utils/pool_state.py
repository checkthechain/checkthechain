from __future__ import annotations

import typing

from ctc import evm
from ctc import rpc
from ctc import spec

from . import pool_metadata
from . import pool_parameters
from . import curve_spec


async def async_get_virtual_price(
    pool: spec.Address,
    *,
    provider: spec.ProviderReference = None,
    block: spec.BlockNumberReference | None = None,
) -> int:
    result = await rpc.async_eth_call(
        to_address=pool,
        function_abi=curve_spec.pool_function_abis['get_virtual_price'],
        function_parameters=[],
        provider=provider,
        block_number=block,
    )

    if not isinstance(result, int):
        raise Exception('invalid rpc result')

    return result


async def async_get_lp_withdrawal(
    pool: spec.Address,
    amount_lp: int,
    *,
    token_withdrawn: spec.Address,
    provider: spec.ProviderReference = None,
) -> int:

    token_index = await pool_metadata.async_get_token_index(
        pool=pool,
        token=token_withdrawn,
        provider=provider,
    )

    result = await rpc.async_eth_call(
        to_address=pool,
        function_abi=curve_spec.pool_function_abis['calc_withdraw_one_coin'],
        function_parameters=[amount_lp, token_index],
        provider=provider,
    )

    if not isinstance(result, int):
        raise Exception('invalid rpc result')

    return result


async def async_get_pool_state(
    pool: spec.Address,
    *,
    n_tokens: int | None = None,
    block: spec.BlockNumberReference | None = None,
    provider: spec.ProviderReference = None,
    normalize: bool = True,
) -> dict[str, typing.Any]:

    total_supply = await evm.async_get_erc20_total_supply(
        token=pool,
        block=block,
        provider=provider,
        normalize=normalize,
    )
    token_addresses = await pool_metadata.async_get_pool_tokens(
        pool,
        n_tokens=n_tokens,
        provider=provider,
    )
    token_balances = await evm.async_get_erc20s_balances(
        wallet=pool,
        tokens=token_addresses,
        block=block,
        provider=provider,
        normalize=normalize,
    )
    A = await pool_parameters.async_get_pool_A(
        pool=pool,
        block=block,
        provider=provider,
    )

    return {
        'lp_total_supply': total_supply,
        'token_balances': token_balances,
        'A': A,
    }


async def async_get_trade(
    pool: spec.Address,
    *,
    token_in: typing.Union[int, spec.Address],
    token_out: typing.Union[int, spec.Address],
    amount_in: typing.Union[int, float],
    input_normalized: bool = True,
    normalize_output: bool = True,
    provider: spec.ProviderReference = None,
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
        function_abi=curve_spec.pool_function_abis['get_dy'],
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

    if not isinstance(amount_out, (int, float)):
        raise Exception('invalid rpc result')

    return amount_out


# async def async_get_swaps():
#     """
#     Events
#     - TokenExchange 0x8b3e96f2b889fa771c53c981b40daf005f63f637f1869f707052d15a3dd97140
#     - TokenExchangeUnderlying 0xd013ca23e77a65003c2c659c5442c00c805371b7fc1ebd4c206c41d1536bd90b
#     """
#     pass
