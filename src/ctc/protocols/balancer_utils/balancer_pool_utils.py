import decimal

import numpy as np
import pandas as pd

from ctc import evm
from ctc import directory
from ctc import rpc
from ctc.evm import rpc_utils


async def async_get_pool_tokens(
    *, pool_address=None, pool_id=None, block=None, vault=None
):

    if vault is None:
        vault = directory.balancer_v2_vault
    if pool_id is None:
        pool_id = async_get_pool_id(pool_address)

    pool_tokens = rpc_utils.eth_call(
        to_address=vault,
        function_name='getPoolTokens',
        function_parameters=[pool_id],
        block_number=block,
        package_named_outputs=True,
    )

    token_names = tuple(
        evm.get_erc20_name(address) for address in pool_tokens['tokens']
    )

    return {
        'token_addresses': pool_tokens['tokens'],
        'token_names': token_names,
    }


def get_pool_swaps(
    pool_address=None, start_block=None, end_block=None, vault=None
):

    if vault is None:
        vault = directory.balancer_v2_vault

    if start_block is None:
        start_block = directory.balancer_blocks['vault_creation']

    swaps = evm.get_events(
        contract_address=vault,
        event_name='Swap',
        start_block=start_block,
        end_block=end_block,
    )

    if pool_address is not None:
        swaps = swaps[swaps['arg__poolId'].str.startswith(pool_address)]

    return swaps


def get_pool_address(pool_id, block=None, vault=None):
    if vault is None:
        vault = directory.balancer_v2_vault

    pool = rpc_utils.eth_call(
        to_address=vault,
        function_name='getPool',
        function_parameters=[pool_id],
        block_number=block,
    )
    return pool[0]


def async_get_pool_id(pool_address, block=None):
    return rpc_utils.eth_call(
        to_address=pool_address,
        function_name='getPoolId',
        block_number=block,
    )


async def async_get_pool_weights(
    pool_address, block=None, blocks=None, normalize=True
):

    if block is not None or block is None and blocks is None:
        weights = await rpc.async_eth_call(
            to_address=pool_address,
            function_name='getNormalizedWeights',
            block_number=block,
        )
        if normalize:
            weights = [weight / 1e18 for weight in weights]
        return weights

    else:
        weights = await rpc.async_batch_eth_call(
            to_address=pool_address,
            function_name='getNormalizedWeights',
            block_numbers=blocks,
            provider={'chunk_size': 100},
        )
        if normalize:
            weights = [
                [block_weight / 1e18 for block_weight in block_weights]
                for block_weights in weights
            ]
        return pd.DataFrame(weights, index=blocks)


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

