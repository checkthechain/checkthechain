from __future__ import annotations

import typing

from ctc import evm
from ctc import spec
from . import uniswap_v2_events


async def async_get_pool_log_deltas(
    pool: spec.Address,
    start_block: typing.Optional[spec.BlockNumberReference] = None,
    normalize: bool = True,
) -> spec.DataFrame:
    import pandas as pd

    if start_block is None:
        start_block = await evm.async_get_contract_creation_block(pool)

    mints = await uniswap_v2_events.async_get_pool_mints(
        pool, start_block=start_block, normalize=normalize
    )
    burns = await uniswap_v2_events.async_get_pool_burns(
        pool, start_block=start_block, normalize=normalize
    )
    swaps = await uniswap_v2_events.async_get_pool_swaps(
        pool, start_block=start_block, normalize=normalize
    )

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

