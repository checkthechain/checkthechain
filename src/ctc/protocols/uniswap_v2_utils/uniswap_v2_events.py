import asyncio

from ctc import evm
from ctc import spec

from . import uniswap_v2_metadata


async def async_get_pool_swaps(
    pool_address,
    start_block=None,
    end_block=None,
    replace_symbols=False,
    normalize=True,
    provider: spec.ProviderSpec = None,
) -> spec.DataFrame:

    if normalize or replace_symbols:
        symbols_task = asyncio.create_task(
            uniswap_v2_metadata.async_get_pool_symbols(
                pool_address, provider=provider
            )
        )
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
    )

    if normalize or replace_symbols:
        symbols = await symbols_task
        decimals = await decimals_task

    # rename columns
    if replace_symbols:
        x_symbol, y_symbol = symbols
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

    # normalize columns
    if normalize:
        x_decimals, y_decimals = decimals
        swaps[columns['arg__amount0In']] = swaps[
            columns['arg__amount0In']
        ].astype(float) / (10 ** x_decimals)
        swaps[columns['arg__amount0Out']] = swaps[
            columns['arg__amount0Out']
        ].astype(float) / (10 ** x_decimals)
        swaps[columns['arg__amount1In']] = swaps[
            columns['arg__amount1In']
        ].astype(float) / (10 ** y_decimals)
        swaps[columns['arg__amount1Out']] = swaps[
            columns['arg__amount1Out']
        ].astype(float) / (10 ** y_decimals)

    return swaps


async def async_get_pool_mints(
    pool_address,
    start_block=None,
    end_block=None,
    # replace_symbols=False,
    # normalize=True,
):
    return evm.get_events(
        event_name='Mint',
        contract_address=pool_address,
        start_block=start_block,
        end_block=end_block,
    )


async def async_get_pool_burns(
    pool_address,
    start_block=None,
    end_block=None,
    # replace_symbols=False,
    # normalize=True,
):
    return evm.get_events(
        event_name='Burn',
        contract_address=pool_address,
        start_block=start_block,
        end_block=end_block,
    )

