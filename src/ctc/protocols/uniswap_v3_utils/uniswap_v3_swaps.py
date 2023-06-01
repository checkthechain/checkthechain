from __future__ import annotations

import asyncio
import typing

from ctc import spec
import ctc.rpc

if typing.TYPE_CHECKING:
    import polars as pl


token0_abi = {
    'inputs': [],
    'name': 'token0',
    'outputs': [{'internalType': 'address', 'name': '', 'type': 'address'}],
    'stateMutability': 'view',
    'type': 'function',
}

token1_abi = {
    'inputs': [],
    'name': 'token1',
    'outputs': [{'internalType': 'address', 'name': '', 'type': 'address'}],
    'stateMutability': 'view',
    'type': 'function',
}

fee_abi = {
    'inputs': [],
    'name': 'fee',
    'outputs': [{'internalType': 'uint24', 'name': '', 'type': 'uint24'}],
    'stateMutability': 'view',
    'type': 'function',
}


async def _async_get_pool_fee(
    pool: str, context: spec.Context | None
) -> int | None:
    try:
        return await ctc.rpc.async_eth_call(
            to_address=pool,
            function_abi=fee_abi,
            context=context,
        )
    except Exception:
        return None


async def async_get_pool_summaries(
    pools: typing.Sequence[str],
    context: spec.Context | None = None,
) -> pl.DataFrame:
    import polars as pl

    # get token0
    coroutines = [
        ctc.rpc.async_eth_call(
            to_address=contract_address,
            function_abi=token0_abi,
            context=context,
        )
        for contract_address in pools
    ]
    token0s = await asyncio.gather(*coroutines)

    # get token1
    coroutines = [
        ctc.rpc.async_eth_call(
            to_address=contract_address,
            function_abi=token1_abi,
            context=context,
        )
        for contract_address in pools
    ]
    token1s = await asyncio.gather(*coroutines)

    # get token0 symbols
    coroutines = [
        ctc.async_get_erc20_symbol(
            token0,
            convert_reverts_to='UNKNOWN',
            context=context,
        )
        for token0 in token0s
    ]
    token0_symbols = await asyncio.gather(*coroutines)

    # get token1 symbols
    coroutines = [
        ctc.async_get_erc20_symbol(
            token1,
            convert_reverts_to='UNKNOWN',
            context=context,
        )
        for token1 in token1s
    ]
    token1_symbols = await asyncio.gather(*coroutines)

    # get token0 decimals
    coroutines = [
        ctc.async_get_erc20_decimals(
            token0,
            convert_reverts_to_none=True,
            context=context,
        )
        for token0 in token0s
    ]
    token0_decimals = await asyncio.gather(*coroutines)

    # get token1 decimals
    coroutines = [
        ctc.async_get_erc20_decimals(
            token1,
            convert_reverts_to_none=True,
            context=context,
        )
        for token1 in token1s
    ]
    token1_decimals = await asyncio.gather(*coroutines)

    # get fees
    coroutines = [
        _async_get_pool_fee(contract_address, context=context)
        for contract_address in pools
    ]
    pool_fees = await asyncio.gather(*coroutines)

    # create DataFrame
    pool_summaries = pl.DataFrame(
        [
            pl.Series(pools).alias('pool'),
            pl.Series(token0_symbols).alias('token0_symbol'),
            pl.Series(token1_symbols).alias('token1_symbol'),
            pl.Series(token0_decimals).alias('token0_decimals'),
            pl.Series(token1_decimals).alias('token1_decimals'),
            pl.Series(token0s).alias('token0_address'),
            pl.Series(token1s).alias('token1_address'),
            pl.Series(pool_fees).alias('pool_fee'),
        ]
    )

    # add pool_name
    pool_summaries = pool_summaries.with_columns(
        (
            pl.col('token0_symbol')
            + '_'
            + pl.col('token1_symbol')
            + '_'
            + (pl.col('pool_fee') / 100).cast(int).cast(str)
        ).alias('pool_name')
    )

    return pool_summaries


async def async_get_swaps_pool_metadata(
    swaps: pl.DataFrame, context: spec.Context = None
) -> pl.DataFrame:
    pools = sorted(swaps['contract_address'].unique().to_list())
    pool_summaries = await async_get_pool_summaries(pools, context=context)
    joined = swaps.join(
        pool_summaries,
        left_on='contract_address',
        right_on='pool',
        how='left',
    )
    return joined[
        [column for column in pool_summaries.columns if column != 'pool']
    ]


default_token_categories = {
    'Stable': {
        '0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48': 'USDC',
        '0xdac17f958d2ee523a2206206994597c13d831ec7': 'USDT',
        '0x6b175474e89094c44da98b954eedeac495271d0f': 'DAI',
    },
    'ETH': {
        '0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2': 'WETH',
    },
    'BTC': {
        '0x2260fac5e5542a773aa44fbcfedf7c193bc2c599': 'WBTC',
    },
}

default_pair_categories = [
    ('Stable', 'Stable', 'Stable-Stable'),
    ('Stable', 'ETH', 'Stable-ETH'),
    ('ETH', 'Stable', 'Stable-ETH'),
    ('Stable', 'BTC', 'Stable-BTC'),
    ('BTC', 'Stable', 'Stable-BTC'),
    ('Stable', 'Other', 'Stable-Other'),
    ('Other', 'Stable', 'Stable-Other'),
    ('ETH', 'ETH', 'ETH-ETH'),
    ('ETH', 'BTC', 'ETH-BTC'),
    ('BTC', 'ETH', 'ETH-BTC'),
    ('ETH', 'Other', 'ETH-Other'),
    ('Other', 'ETH', 'ETH-Other'),
    ('BTC', 'BTC', 'BTC-BTC'),
    ('BTC', 'Other', 'BTC-Other'),
    ('Other', 'BTC', 'BTC-Other'),
    ('Other', 'Other', 'Other-Other'),
]


def get_swaps_pair_categories(
    swaps: spec.DataFrame,
    token_categories: typing.Mapping[str, typing.Mapping[str, str]]
    | None = None,
    pair_categories: typing.Sequence[tuple[str, str, str]] | None = None,
) -> spec.DataFrame:
    import polars as pl

    if token_categories is None:
        token_categories = default_token_categories
    if pair_categories is None:
        pair_categories = default_pair_categories

    df = pl.DataFrame(
        [
            [category, address]
            for category, tokens in token_categories.items()
            for address in tokens
        ],
        orient='row',
        schema=['category', 'address'],
    )

    cats = swaps.join(
        df.rename({'address': 'token0_address', 'category': 'token0_category'}),
        on='token0_address',
        how='left',
    ).join(
        df.rename({'address': 'token1_address', 'category': 'token1_category'}),
        on='token1_address',
        how='left',
    )
    cats = cats.select(
        pl.col('token0_category').fill_null('Other'),
        pl.col('token1_category').fill_null('Other'),
    )

    df = pl.DataFrame(
        pair_categories,
        orient='row',
        schema=['token0_category', 'token1_category', 'pair_category'],
    )

    return cats.join(df, on=['token0_category', 'token1_category'], how='left')

