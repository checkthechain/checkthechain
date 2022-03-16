from __future__ import annotations

import asyncio
import typing

from ctc import evm
from ctc import spec
from . import uniswap_v2_events
from . import uniswap_v2_state


async def async_get_pool_log_deltas(
    pool: spec.Address,
    start_block: typing.Optional[spec.BlockNumberReference] = None,
    end_block: typing.Optional[spec.BlockNumberReference] = None,
    normalize: bool = True,
    include_initial_state: bool = True,
) -> spec.DataFrame:
    import pandas as pd

    # get start_block and initial conditions
    if start_block is None:
        start_block = await evm.async_get_contract_creation_block(pool)
        initial_point_task = None
    else:
        if include_initial_state:
            coroutine = uniswap_v2_state.async_get_pool_state(
                pool,
                block=start_block,
                normalize=normalize,
            )
            initial_point_task = asyncio.create_task(coroutine)
        else:
            initial_point_task = None

    # get mints, burns, and swaps
    mints_task = uniswap_v2_events.async_get_pool_mints(
        pool,
        start_block=start_block,
        end_block=end_block,
        normalize=normalize,
    )
    burns_task = uniswap_v2_events.async_get_pool_burns(
        pool,
        start_block=start_block,
        end_block=end_block,
        normalize=normalize,
    )
    swaps_task = uniswap_v2_events.async_get_pool_swaps(
        pool,
        start_block=start_block,
        end_block=end_block,
        normalize=normalize,
    )
    mints, burns, swaps = await asyncio.gather(
        mints_task, burns_task, swaps_task
    )

    # gather as DataFrames
    dfs = [
        pd.DataFrame(
            {
                'event': 'Mint',
                'delta_token0': mints['arg__amount0'],
                'delta_token1': mints['arg__amount1'],
            }
        ),
        pd.DataFrame(
            {
                'event': 'Burn',
                'delta_token0': -burns['arg__amount0'],
                'delta_token1': -burns['arg__amount1'],
            }
        ),
        pd.DataFrame(
            {
                'event': 'Swap',
                'delta_token0': swaps['x_sold'] - swaps['x_bought'],
                'delta_token1': swaps['y_sold'] - swaps['y_bought'],
            },
        ),
    ]

    # add initial point
    if initial_point_task is not None:
        initial_point = await initial_point_task
        initial_point_df = pd.DataFrame(
            {
                'event': 'Initial',
                'delta_token0': initial_point['x_reserves'],
                'delta_token1': initial_point['y_reserves'],
            }
        )
        dfs.append(initial_point_df)

    df = pd.concat(dfs)
    df = df.sort_index()

    return df


async def async_get_pool_transaction_deltas(
    pool: typing.Optional[spec.Address] = None,
    log_deltas: typing.Optional[spec.DataFrame] = None,
    **log_delta_kwargs: typing.Any
) -> spec.DataFrame:

    if log_deltas is None:
        if pool is None:
            raise Exception('must specify pool or log_deltas')
        log_deltas = await async_get_pool_log_deltas(pool, **log_delta_kwargs)

    transaction_deltas = log_deltas.groupby(
        ['block_number', 'transaction_index']
    ).sum()

    return transaction_deltas


async def async_get_pool_block_deltas(
    pool: typing.Optional[spec.Address] = None,
    log_deltas: typing.Optional[spec.DataFrame] = None,
    **log_delta_kwargs: typing.Any
) -> spec.DataFrame:

    if log_deltas is None:
        if pool is None:
            raise Exception('must specify pool or log_deltas')
        log_deltas = await async_get_pool_log_deltas(pool, **log_delta_kwargs)

    block_deltas = log_deltas.groupby(['block_number']).sum()

    return block_deltas


async def async_get_pool_state_per_log(
    pool: typing.Optional[spec.Address] = None,
    log_deltas: typing.Optional[spec.DataFrame] = None,
    **log_delta_kwargs: typing.Any
) -> spec.DataFrame:

    if log_deltas is None:
        if pool is None:
            raise Exception('must specify pool or log_deltas')
        log_deltas = await async_get_pool_log_deltas(pool, **log_delta_kwargs)

    state_per_log = log_deltas[['delta_token0', 'delta_token1']].cumsum()
    state_per_log.columns = ['token0_reserves', 'token1_reserves']

    _put_price_in_state(state_per_log)

    return state_per_log


async def async_get_pool_state_per_transaction(
    pool: typing.Optional[spec.Address] = None,
    log_deltas: typing.Optional[spec.DataFrame] = None,
    **log_delta_kwargs: typing.Any
) -> spec.DataFrame:

    if log_deltas is None:
        if pool is None:
            raise Exception('must specify pool or log_deltas')
        log_deltas = await async_get_pool_log_deltas(pool, **log_delta_kwargs)

    transaction_deltas = await async_get_pool_transaction_deltas(
        log_deltas=log_deltas, **log_delta_kwargs
    )

    state_per_transaction = transaction_deltas[
        ['delta_token0', 'delta_token1']
    ].cumsum()
    state_per_transaction.columns = ['token0_reserves', 'token1_reserves']

    _put_price_in_state(state_per_transaction)

    return state_per_transaction


async def async_get_pool_state_per_block(
    pool: typing.Optional[spec.Address] = None,
    interpolate: bool = False,
    log_deltas: typing.Optional[spec.DataFrame] = None,
    **log_delta_kwargs: typing.Any
) -> spec.DataFrame:

    if log_deltas is None:
        if pool is None:
            raise Exception('must specify pool or log_deltas')
        log_deltas = await async_get_pool_log_deltas(pool, **log_delta_kwargs)

    block_deltas = await async_get_pool_block_deltas(
        log_deltas=log_deltas, **log_delta_kwargs
    )

    state_per_block = block_deltas[['delta_token0', 'delta_token1']].cumsum()
    state_per_block.columns = ['token0_reserves', 'token1_reserves']

    _put_price_in_state(state_per_block)

    if interpolate:
        from ctc.toolbox import pd_utils

        state_per_block = pd_utils.interpolate_dataframe(state_per_block)

    return state_per_block


def _put_price_in_state(state: spec.DataFrame) -> None:
    state['price_0_per_1'] = state['token0_reserves'] / state['token1_reserves']
    state['price_1_per_0'] = state['token1_reserves'] / state['token0_reserves']

