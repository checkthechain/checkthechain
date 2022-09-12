from __future__ import annotations

import typing

from ctc import evm
from ctc import spec

from . import uniswap_v2_metadata
from . import uniswap_v2_spec

if typing.TYPE_CHECKING:
    import tooltime

    from typing_extensions import Literal


async def async_get_pool_swaps(
    pool: spec.Address,
    *,
    start_block: typing.Optional[spec.BlockNumberReference] = None,
    end_block: typing.Optional[spec.BlockNumberReference] = None,
    start_time: tooltime.Timestamp | None = None,
    end_time: tooltime.Timestamp | None = None,
    include_timestamps: bool = False,
    include_prices: bool = False,
    include_volumes: bool = False,
    label: Literal['index', 'symbol', 'address'] = 'index',
    normalize: bool = True,
    provider: spec.ProviderReference = None,
    verbose: bool = False,
) -> spec.DataFrame:

    from ctc.toolbox.defi_utils import dex_utils

    return await dex_utils.UniswapV2DEX.async_get_pool_trades(
        pool=pool,
        start_block=start_block,
        end_block=end_block,
        start_time=start_time,
        end_time=end_time,
        include_timestamps=include_timestamps,
        include_prices=include_prices,
        include_volumes=include_volumes,
        label=label,
        normalize=normalize,
        provider=provider,
        verbose=verbose,
    )


async def async_get_pool_mints(
    pool_address: spec.Address,
    *,
    start_block: typing.Optional[spec.BlockNumberReference] = None,
    end_block: typing.Optional[spec.BlockNumberReference] = None,
    start_time: tooltime.Timestamp | None = None,
    end_time: tooltime.Timestamp | None = None,
    include_timestamps: bool = False,
    replace_symbols: bool = False,
    normalize: bool = True,
    provider: spec.ProviderReference = None,
    verbose: bool = False,
) -> spec.DataFrame:
    import asyncio

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
        event_abi=uniswap_v2_spec.pool_event_abis['Mint'],
        contract_address=pool_address,
        start_block=start_block,
        end_block=end_block,
        start_time=start_time,
        end_time=end_time,
        include_timestamps=include_timestamps,
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
    pool_address: spec.Address,
    *,
    start_block: typing.Optional[spec.BlockNumberReference] = None,
    end_block: typing.Optional[spec.BlockNumberReference] = None,
    start_time: tooltime.Timestamp | None = None,
    end_time: tooltime.Timestamp | None = None,
    include_timestamps: bool = False,
    replace_symbols: bool = False,
    normalize: bool = True,
    provider: spec.ProviderReference = None,
    verbose: bool = False,
) -> spec.DataFrame:
    import asyncio

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
        event_abi=uniswap_v2_spec.pool_event_abis['Burn'],
        contract_address=pool_address,
        start_block=start_block,
        end_block=end_block,
        start_time=start_time,
        end_time=end_time,
        include_timestamps=include_timestamps,
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
