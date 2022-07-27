from __future__ import annotations

import typing

from ctc import evm
from ctc import rpc
from ctc import spec

from . import curve_spec
from . import pool_metadata
from . import pool_state


async def async_get_metapool_trade(
    metapool: spec.Address,
    *,
    token_sold: typing.Union[spec.Address, str],
    token_bought: typing.Union[spec.Address, str],
    amount_sold: typing.Union[int, float],
    input_normalized: bool = True,
    normalize_output: bool = True,
    provider: spec.ProviderReference = None,
    parent_pool: typing.Optional[spec.Address] = None,
    parent_lp: typing.Optional[spec.Address] = None,
    parent_coins: typing.Optional[list[str]] = None,
) -> curve_spec.CurveTrade:

    if parent_pool is None and parent_lp is None:
        parent_pool = curve_spec.three_pool
        parent_lp = curve_spec.three_pool_lp
        parent_coins = curve_spec.three_pool_coins
    if parent_pool is None or parent_lp is None or parent_coins is None:
        raise Exception('must specify more parent parameters')

    metadata = await pool_metadata.async_get_pool_metadata(
        pool=metapool,
        provider=provider,
    )

    if token_bought in parent_coins:

        sold_index = await pool_metadata.async_get_token_index(
            pool=metapool, token=token_sold, metadata=metadata
        )
        bought_index = await pool_metadata.async_get_token_index(
            pool=metapool, token=parent_lp, metadata=metadata
        )

        if input_normalized:
            amount_sold *= 10 ** metadata['token_decimals'][sold_index]

        function_abi: spec.FunctionABI = {
            'inputs': [
                {
                    'name': 'i',
                    'type': 'int128',
                },
                {
                    'name': 'j',
                    'type': 'int128',
                },
                {
                    'name': 'dx',
                    'type': 'uint256',
                },
            ],
            'name': 'get_dy',
            'outputs': [
                {
                    'name': '',
                    'type': 'uint256',
                },
            ],
            'stateMutability': 'view',
            'type': 'function',
        }

        lp_bought = await rpc.async_eth_call(
            to_address=metapool,
            function_abi=function_abi,
            function_parameters=[sold_index, bought_index, amount_sold],
            provider=provider,
        )

        amount_bought = await pool_state.async_get_lp_withdrawal(
            pool=parent_pool,
            amount_lp=lp_bought,
            token_withdrawn=token_bought,
            provider=provider,
        )

        if normalize_output:
            # bought token can be different from lp token
            bought_decimals = await evm.async_get_erc20_decimals(
                metadata['token_addresses'][bought_index],
                provider=provider,
            )
            amount_bought /= 10 ** bought_decimals
            amount_sold /= 10 ** metadata['token_decimals'][sold_index]

    elif token_sold in parent_coins:

        sold_index = await pool_metadata.async_get_token_index(
            pool=metapool, token=parent_lp, metadata=metadata
        )
        bought_index = await pool_metadata.async_get_token_index(
            pool=metapool, token=token_bought, metadata=metadata
        )

        raise NotImplementedError()

    else:
        raise Exception('could not determine token indices')

    return {
        'token_sold': token_sold,
        'token_bought': token_bought,
        'amount_sold': amount_sold,
        'amount_bought': amount_bought,
    }
