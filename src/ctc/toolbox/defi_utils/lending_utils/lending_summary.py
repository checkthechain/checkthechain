from __future__ import annotations

import asyncio
import typing
import types

import pandas as pd
import tooltime

from ctc import evm
from ctc import spec


async def async_get_lending_flows(
    wallet: spec.Address,
    pool_token: spec.ERC20Reference,
    *,
    protocol: typing.Literal['aave', 'compound', 'rari'],
    wallet_deposits: spec.DataFrame | None = None,
    deposits: spec.DataFrame | None = None,
    wallet_withdrawals: spec.DataFrame | None = None,
    withdrawals: spec.DataFrame | None = None,
    include_latest: bool = True,
    provider: spec.ProviderReference = None,
    replace_symbols: bool = True,
    normalize: bool = True,
    include_rewards: bool = True,
) -> spec.DataFrame:

    if protocol == 'aave':
        from ctc.protocols import aave_v2_utils

        protocol_module: types.ModuleType = aave_v2_utils
    elif protocol == 'compound':
        from ctc.protocols import compound_utils

        protocol_module = compound_utils
    elif protocol == 'rari':
        from ctc.protocols import rari_utils

        protocol_module = rari_utils
    else:
        raise Exception('unknown protocol: ' + str(protocol))

    df = await _async_create_raw_wallet_flows_df(
        wallet=wallet,
        wallet_deposits=wallet_deposits,
        deposits=deposits,
        wallet_withdrawals=wallet_withdrawals,
        withdrawals=withdrawals,
        include_latest=include_latest,
        provider=provider,
    )

    underlying = await protocol_module.async_get_underlying_asset(
        pool_token=pool_token,
        provider=provider,
    )

    # add time data
    blocks = df.index.values
    blocks_before = blocks - 1

    # queue tasks
    timestamps_coroutine = evm.async_get_block_timestamps(
        blocks=blocks,
        provider=provider,
    )
    timestamps_task = asyncio.create_task(timestamps_coroutine)
    pool_token_balances_before_coroutine = (
        evm.async_get_erc20_balance_by_block(
            token=pool_token,
            wallet=wallet,
            blocks=blocks_before,
            provider=provider,
        )
    )
    pool_token_balances_before_task = asyncio.create_task(
        pool_token_balances_before_coroutine
    )
    pool_token_balances_after_coroutine = (
        evm.async_get_erc20_balance_by_block(
            token=pool_token,
            wallet=wallet,
            blocks=blocks,
            provider=provider,
        )
    )
    pool_token_balances_after_task = asyncio.create_task(
        pool_token_balances_after_coroutine
    )
    asset_prices_coroutine = protocol_module.async_get_asset_price_by_block(
        asset=underlying,
        blocks=blocks,
        provider=provider,
    )
    asset_prices_task = asyncio.create_task(asset_prices_coroutine)

    # queue optional tasks
    if include_rewards:
        reward_coroutine = protocol_module.async_compute_wallet_rewards(
            wallet=wallet,
            blocks=blocks,
            provider=provider,
            replace_symbol=replace_symbols,
        )
        reward_task = asyncio.create_task(reward_coroutine)
    if normalize:
        decimals_coroutine = evm.async_get_erc20_decimals(
            underlying,
            provider=provider,
        )
        decimals_task = asyncio.create_task(decimals_coroutine)
    if replace_symbols:
        underlying_symbol_coroutine = evm.async_get_erc20_symbol(
            underlying,
            provider=provider,
        )
        underlying_symbol_task = asyncio.create_task(
            underlying_symbol_coroutine
        )
        pool_token_coroutine = evm.async_get_erc20_symbol(
            pool_token,
            provider=provider,
        )
        pool_token_symbol_task = asyncio.create_task(pool_token_coroutine)

    # normalize deposits and withdrawals
    if normalize:
        decimals = await decimals_task
        df['asset_deposit'] /= 10 ** decimals
        df['asset_withdrawal'] /= 10 ** decimals

    # compute time columns
    timestamps = await timestamps_task
    df.insert(loc=0, column='timestamp', value=timestamps)  # type: ignore
    df.insert(
        loc=1,
        column='time',
        value=df['timestamp'].map(tooltime.timestamp_to_iso),
    )

    # add pool token balances
    df['pool_token_balance_before'] = await pool_token_balances_before_task
    df['pool_token_balance_after'] = await pool_token_balances_after_task

    # add underlying balances
    df['asset_balance_before'] = df['pool_token_balance_before']
    df['asset_balance_after'] = df['pool_token_balance_after']

    # add asset price
    df['asset_price'] = await asset_prices_task
    df['asset_balance_usd'] = df['asset_balance_after'] * df['asset_price']

    # add rewards
    rewards = await reward_task
    for key, value in rewards.items():
        df[key] = value

    # replace symbols
    if replace_symbols:
        rename_columns = {}
        underlying_symbol = await underlying_symbol_task
        pool_token_symbol = await pool_token_symbol_task
        for column in df.columns:
            if 'asset' in column:
                rename_columns[column] = column.replace(
                    'asset', underlying_symbol
                )
            if 'pool_token' in column:
                rename_columns[column] = column.replace(
                    'pool_token', pool_token_symbol
                )
        df = df.rename(columns=rename_columns)

    return df


async def _async_create_raw_wallet_flows_df(
    *,
    wallet: spec.Address,
    wallet_deposits: spec.DataFrame | None = None,
    deposits: spec.DataFrame | None = None,
    wallet_withdrawals: spec.DataFrame | None = None,
    withdrawals: spec.DataFrame | None = None,
    include_latest: bool = True,
    provider: spec.ProviderReference = None,
) -> spec.DataFrame:

    from ctc.protocols import aave_v2_utils

    no_deposits = wallet_deposits is None and deposits is None
    no_withdrawals = wallet_withdrawals is None and withdrawals is None
    if no_deposits and not no_withdrawals:
        deposits = await aave_v2_utils.async_get_deposits()
    elif not no_deposits and no_withdrawals:
        withdrawals = await aave_v2_utils.async_get_withdrawals()
    elif no_deposits and no_withdrawals:
        deposits, withdrawals = await asyncio.gather(
            aave_v2_utils.async_get_deposits(provider=provider),
            aave_v2_utils.async_get_withdrawals(provider=provider),
        )

    wallet = wallet.lower()
    if wallet_deposits is None:
        if deposits is None:
            raise Exception('could not determine deposits')
        wallet_deposits = deposits[deposits['arg__user'] == wallet]
    if isinstance(wallet_deposits.index, pd.MultiIndex):
        wallet_deposits = wallet_deposits.groupby(level='block_number').sum()
    if isinstance(wallet_deposits, pd.DataFrame):
        wallet_deposits_series = wallet_deposits['arg__amount']
    if wallet_withdrawals is None:
        if withdrawals is None:
            raise Exception('could not determine withdrawals')
        wallet_withdrawals = withdrawals[withdrawals['arg__user'] == wallet]
    if isinstance(wallet_withdrawals.index, pd.MultiIndex):
        wallet_withdrawals = wallet_withdrawals.groupby(
            level='block_number'
        ).sum()
    if isinstance(wallet_withdrawals, pd.DataFrame):
        wallet_withdrawals_series = wallet_withdrawals['arg__amount']

    raw_data = {
        'asset_deposit': wallet_deposits_series,
        'asset_withdrawal': wallet_withdrawals_series,
    }
    raw_df = pd.DataFrame(raw_data)
    raw_df = raw_df.fillna(0)

    if include_latest:
        block = await evm.async_get_latest_block_number(provider=provider)
        raw_df.loc[block] = [0, 0]

    return raw_df
