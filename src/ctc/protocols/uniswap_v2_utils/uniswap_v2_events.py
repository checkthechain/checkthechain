from __future__ import annotations

import asyncio
import typing

from ctc import evm
from ctc import spec

from . import uniswap_v2_metadata


async def async_get_pool_swaps(
    pool_address: spec.Address,
    start_block: typing.Optional[spec.BlockNumberReference] = None,
    end_block: typing.Optional[spec.BlockNumberReference] = None,
    replace_symbols: bool = False,
    normalize: bool = True,
    provider: spec.ProviderSpec = None,
    verbose=False,
) -> spec.DataFrame:

    if replace_symbols:
        symbols_task = asyncio.create_task(
            uniswap_v2_metadata.async_get_pool_symbols(
                pool_address, provider=provider
            )
        )
    if normalize:
        decimals_task = asyncio.create_task(
            uniswap_v2_metadata.async_get_pool_decimals(
                pool_address, provider=provider
            )
        )

    swaps = await evm.async_get_events(
        event_name='Swap',
        contract_address=pool_address,
        start_block=start_block,
        end_block=end_block,
        provider=provider,
        verbose=verbose,
    )
    swaps['arg__amount0In'] = swaps['arg__amount0In'].map(int)
    swaps['arg__amount0Out'] = swaps['arg__amount0Out'].map(int)
    swaps['arg__amount1In'] = swaps['arg__amount1In'].map(int)
    swaps['arg__amount1Out'] = swaps['arg__amount1Out'].map(int)

    # normalize columns
    if normalize:
        x_decimals, y_decimals = await decimals_task
        swaps['arg__amount0In'] = await evm.async_normalize_erc20_quantities(
            quantities=swaps['arg__amount0In'].astype(float),  # type: ignore
            decimals=x_decimals,
        )
        swaps['arg__amount0Out'] = await evm.async_normalize_erc20_quantities(
            quantities=swaps['arg__amount0Out'].astype(float),  # type: ignore
            decimals=x_decimals,
        )
        swaps['arg__amount1In'] = await evm.async_normalize_erc20_quantities(
            quantities=swaps['arg__amount1In'].astype(float),  # type: ignore
            decimals=y_decimals,
        )
        swaps['arg__amount1Out'] = await evm.async_normalize_erc20_quantities(
            quantities=swaps['arg__amount1Out'].astype(float),  # type: ignore
            decimals=y_decimals,
        )

    # rename columns
    if replace_symbols:
        x_symbol, y_symbol = await symbols_task
    else:
        x_symbol = 'x'
        y_symbol = 'y'
    columns = {
        'arg__amount0In': x_symbol + '_sold',
        'arg__amount0Out': x_symbol + '_bought',
        'arg__amount1In': y_symbol + '_sold',
        'arg__amount1Out': y_symbol + '_bought',
    }
    swaps = swaps.rename(columns=columns)

    return swaps


async def async_get_pool_mints(
    pool_address,
    start_block=None,
    end_block=None,
    replace_symbols=False,
    normalize=True,
    provider=None,
    verbose=False,
):
    if normalize:
        decimals_task = asyncio.create_task(
            uniswap_v2_metadata.async_get_pool_decimals(
                pool_address, provider=provider
            )
        )
    if replace_symbols:
        symbols_task = asyncio.create_task(
            uniswap_v2_metadata.async_get_pool_symbols(
                pool_address, provider=provider
            )
        )

    mints = await evm.async_get_events(
        event_name='Mint',
        contract_address=pool_address,
        start_block=start_block,
        end_block=end_block,
        provider=provider,
        verbose=verbose,
    )
    mints['arg__amount0'] = mints['arg__amount0'].map(int)
    mints['arg__amount1'] = mints['arg__amount1'].map(int)

    if normalize:
        decimals0, decimals1 = await decimals_task
        mints['arg__amount0'] = await evm.async_normalize_erc20_quantities(
            quantities=mints['arg__amount0'].astype(float),
            decimals=decimals0,
            provider=provider,
        )
        mints['arg__amount1'] = await evm.async_normalize_erc20_quantities(
            quantities=mints['arg__amount1'].astype(float),
            decimals=decimals1,
            provider=provider,
        )

    if replace_symbols:
        symbol0, symbol1 = await symbols_task
        new_names = {
            'arg__amount0': symbol0 + '_amount',
            'arg__amount1': symbol1 + '_amount',
        }
        mints = mints.rename(columns=new_names)

    return mints


async def async_get_pool_burns(
    pool_address,
    start_block=None,
    end_block=None,
    replace_symbols=False,
    normalize=True,
    provider=None,
    verbose=False
):

    if normalize:
        decimals_task = asyncio.create_task(
            uniswap_v2_metadata.async_get_pool_decimals(
                pool_address, provider=provider
            )
        )
    if replace_symbols:
        symbols_task = asyncio.create_task(
            uniswap_v2_metadata.async_get_pool_symbols(
                pool_address, provider=provider
            )
        )

    burns = await evm.async_get_events(
        event_name='Burn',
        contract_address=pool_address,
        start_block=start_block,
        end_block=end_block,
        provider=provider,
        verbose=verbose,
    )
    burns['arg__amount0'] = burns['arg__amount0'].map(int)
    burns['arg__amount1'] = burns['arg__amount1'].map(int)

    if normalize:
        decimals0, decimals1 = await decimals_task
        burns['arg__amount0'] = await evm.async_normalize_erc20_quantities(
            quantities=burns['arg__amount0'].astype(float),
            decimals=decimals0,
            provider=provider,
        )
        burns['arg__amount1'] = await evm.async_normalize_erc20_quantities(
            quantities=burns['arg__amount1'].astype(float),
            decimals=decimals1,
            provider=provider,
        )

    if replace_symbols:
        symbol0, symbol1 = await symbols_task
        new_names = {
            'arg__amount0': symbol0 + '_amount',
            'arg__amount1': symbol1 + '_amount',
        }
        burns = burns.rename(columns=new_names)

    return burns

