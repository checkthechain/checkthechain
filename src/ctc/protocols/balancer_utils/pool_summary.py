import decimal

import numpy as np
import pandas as pd

from ctc import directory
from ctc import evm
from ctc import spec

from . import pool_metadata
from . import pool_state


async def async_summarize_pool_state(balancer_pool, block='latest'):

    block = await evm.async_block_number_to_int(block)

    pool_tokens_coroutine = await pool_metadata.async_get_pool_tokens(
        pool_address=balancer_pool,
        block=block,
    )
    pool_fees_coroutine = await pool_state.async_get_pool_fees(
        pool_address=balancer_pool,
        block=block,
    )
    pool_weights_coroutine = await pool_state.async_get_pool_weights(
        pool_address=balancer_pool,
        block=block,
    )
    pool_balances_coroutine = await pool_state.async_get_pool_balances(
        pool_address=balancer_pool,
        block=block,
    )

    return {
        'pool_tokens': pool_tokens_coroutine,
        'pool_fees': pool_fees_coroutine,
        'pool_weights': pool_weights_coroutine,
        'pool_balances': pool_balances_coroutine,
        'block': block,
    }


async def async_get_pool_swaps(
    pool_address=None, start_block=None, end_block=None, vault=None
) -> spec.DataFrame:

    if vault is None:
        vault = directory.get_address(name='Vault', label='balancer')

    if start_block is None:
        start_block = directory.get_address_first_block(
            name='Vault', label='balancer'
        )

    swaps = await evm.async_get_events(
        contract_address=vault,
        event_name='Swap',
        start_block=start_block,
        end_block=end_block,
    )

    if pool_address is not None:
        swaps = swaps[swaps['arg__poolId'].str.startswith(pool_address)]

    return swaps


def summarize_pool_swaps(swaps, weights, as_dataframe=True):

    trade_pairs = set()
    for i, row in swaps[['arg__tokenIn', 'arg__tokenOut']].iterrows():
        trade_pairs.add(tuple(row.values))

    pair_data = {}
    for token_in, token_out in trade_pairs:

        mask = (swaps['arg__tokenIn'] == token_in) & (
            swaps['arg__tokenOut'] == token_out
        )
        pair_swaps = swaps[mask]
        pair_weights = weights[mask.values]
        in_amounts = pair_swaps['arg__amountIn'].map(
            decimal.Decimal
        ) / decimal.Decimal('1e18')
        out_amounts = pair_swaps['arg__amountOut'].map(
            decimal.Decimal
        ) / decimal.Decimal('1e18')
        price_in_per_out = in_amounts / out_amounts
        price_out_per_in = out_amounts / in_amounts
        cummulative_in_amount = np.cumsum(in_amounts)
        cummulative_out_amount = np.cumsum(out_amounts)
        cummulative_price_in_per_out = (
            cummulative_in_amount / cummulative_out_amount
        )
        cummulative_price_out_per_in = (
            cummulative_out_amount / cummulative_in_amount
        )

        data = {
            'in_amounts': in_amounts,
            'out_amounts': out_amounts,
            'price_in_per_out': price_in_per_out,
            'price_out_per_in': price_out_per_in,
            'cummulative_in_amount': cummulative_in_amount,
            'cummulative_out_amount': cummulative_out_amount,
            'cummulative_price_in_per_out': cummulative_price_in_per_out,
            'cummulative_price_out_per_in': cummulative_price_out_per_in,
        }

        for c, weight_column in enumerate(pair_weights.columns):
            data['weight_' + str(c)] = pair_weights[weight_column].values

        if as_dataframe:
            data = pd.DataFrame(data)

        pair_data[(token_in, token_out)] = data

    return pair_data

