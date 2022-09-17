from __future__ import annotations

import decimal
import typing
from typing_extensions import TypedDict

from ctc import evm
from ctc import spec

from . import balancer_spec
from . import pool_metadata
from . import pool_state

if typing.TYPE_CHECKING:
    import tooltime


class BalancerPoolState(TypedDict):
    block: int
    pool_tokens: typing.Sequence[spec.Address]
    pool_fees: typing.Union[int, float]
    pool_weights: typing.Union[
        dict[spec.ContractAddress, int],
        dict[spec.ContractAddress, float],
    ]
    pool_balances: typing.Union[
        dict[spec.Address, int],
        dict[spec.Address, float],
    ]


async def async_summarize_pool_state(
    pool_address: spec.Address,
    block: spec.BlockNumberReference = 'latest',
) -> BalancerPoolState:

    block = await evm.async_block_number_to_int(block)

    pool_tokens_coroutine = await pool_metadata.async_get_pool_tokens(
        pool_address=pool_address,
        block=block,
    )
    pool_fees_coroutine = await pool_state.async_get_pool_fees(
        pool_address=pool_address,
        block=block,
    )
    pool_weights_coroutine = await pool_state.async_get_pool_weights(
        pool_address=pool_address,
        block=block,
    )
    pool_balances_coroutine = await pool_state.async_get_pool_balances(
        pool_address=pool_address,
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
    pool_address: typing.Optional[spec.Address] = None,
    *,
    start_block: typing.Optional[spec.BlockNumberReference] = None,
    end_block: typing.Optional[spec.BlockNumberReference] = None,
    start_time: tooltime.Timestamp | None = None,
    end_time: tooltime.Timestamp | None = None,
    include_timestamps: bool = False,
) -> spec.DataFrame:

    event_abi: spec.EventABI = {
        'anonymous': False,
        'inputs': [
            {
                'indexed': True,
                'internalType': 'bytes32',
                'name': 'poolId',
                'type': 'bytes32',
            },
            {
                'indexed': True,
                'internalType': 'contract IERC20',
                'name': 'tokenIn',
                'type': 'address',
            },
            {
                'indexed': True,
                'internalType': 'contract IERC20',
                'name': 'tokenOut',
                'type': 'address',
            },
            {
                'indexed': False,
                'internalType': 'uint256',
                'name': 'amountIn',
                'type': 'uint256',
            },
            {
                'indexed': False,
                'internalType': 'uint256',
                'name': 'amountOut',
                'type': 'uint256',
            },
        ],
        'name': 'Swap',
        'type': 'event',
    }

    vault = balancer_spec.vault

    start_block, end_block = await evm.async_resolve_block_range(
        start_block=start_block,
        end_block=end_block,
        start_time=start_time,
        end_time=end_time,
        allow_none=True,
    )

    if start_block is None:
        start_block = await evm.async_get_contract_creation_block(vault)

    swaps = await evm.async_get_events(
        contract_address=vault,
        event_abi=event_abi,
        start_block=start_block,
        end_block=end_block,
        include_timestamps=include_timestamps,
        verbose=False,
    )

    if pool_address is not None:
        swaps = swaps[swaps['arg__poolId'].str.startswith(pool_address)]

    return swaps


def summarize_pool_swaps(
    swaps: spec.DataFrame,
    weights: spec.DataFrame,
    *,
    as_dataframe: bool = True,
) -> typing.Mapping[tuple[str, str], spec.DataFrame]:

    import numpy as np

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
            import pandas as pd

            df = pd.DataFrame(data)

        pair_data[(token_in, token_out)] = df

    return pair_data
