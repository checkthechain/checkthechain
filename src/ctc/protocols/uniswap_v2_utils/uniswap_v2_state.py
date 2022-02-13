import asyncio
import typing

from ctc import evm
from ctc import spec
from ctc.toolbox import nested_utils

from . import uniswap_v2_metadata
from . import uniswap_v2_spec


async def replace_pool_state_symbols(
    pool_state: typing.Mapping,
    *,
    pool: spec.Address = None,
    symbols: typing.Optional[typing.Sequence[str]] = None,
    provider: spec.ProviderSpec = None,
) -> typing.Mapping:

    if symbols is None:
        if pool is None:
            raise Exception('must specify pool or symbols')
        symbols = await uniswap_v2_metadata.async_get_pool_symbols(
            pool=pool, provider=provider
        )

    x_symbol, y_symbol = symbols

    return {
        x_symbol + '_reserves': pool_state['x_reserves'],
        y_symbol + '_reserves': pool_state['y_reserves'],
        'lp_total_supply': pool_state['lp_total_supply'],
    }


async def async_get_pool_state(
    pool: spec.Address,
    *,
    block: spec.BlockNumberReference = 'latest',
    provider: spec.ProviderSpec = None,
    normalize: bool = True,
) -> uniswap_v2_spec.PoolState:

    block = await evm.async_block_number_to_int(block, provider=provider)

    # reserves
    token_x, token_y = await uniswap_v2_metadata.async_get_pool_tokens(
        pool=pool, provider=provider
    )
    reserves_coroutine = evm.async_get_erc20s_balance_of(
        address=pool,
        tokens=[token_x, token_y],
        block=block,
        provider=provider,
        normalize=normalize,
    )
    reserves_task = asyncio.create_task(reserves_coroutine)

    # total supply
    lp_total_supply_coroutine = evm.async_get_erc20_total_supply(
        token=pool,
        block=block,
        provider=provider,
        normalize=normalize,
    )
    lp_total_supply_task = asyncio.create_task(lp_total_supply_coroutine)

    # metadata
    if normalize:
        decimals_coroutine = uniswap_v2_metadata.async_get_pool_decimals(
            pool=pool,
            provider=provider,
        )
        decimals_task = asyncio.create_task(decimals_coroutine)

    # await results
    token_x_reserves, token_y_reserves = await reserves_task
    lp_total_supply = await lp_total_supply_task

    output: uniswap_v2_spec.PoolState = {
        'x_reserves': token_x_reserves,
        'y_reserves': token_y_reserves,
        'lp_total_supply': lp_total_supply,
    }
    return output


async def async_get_pool_state_by_block(
    pool: spec.Address,
    *,
    blocks: typing.Sequence[spec.BlockNumberReference],
    provider: spec.ProviderSpec = None,
    normalize: bool = True,
) -> uniswap_v2_spec.PoolStateByBlock:

    if normalize:
        decimals_coroutine = uniswap_v2_metadata.async_get_pool_decimals(
            pool=pool,
            provider=provider,
        )
        decimals_task = asyncio.create_task(decimals_coroutine)

    coroutines = [
        async_get_pool_state(
            pool=pool,
            block=block,
            provider=provider,
            normalize=False,
        )
        for block in blocks
    ]
    results: list[uniswap_v2_spec.PoolState] = await asyncio.gather(*coroutines)

    output: uniswap_v2_spec.PoolStateByBlock = (
        nested_utils.list_of_dicts_to_dict_of_lists(results)  # type: ignore
    )

    if normalize:

        x_decimals, y_decimals = await decimals_task

        output['x_reserves'] = [
            item / (x_decimals ** 18) for item in output['x_reserves']
        ]
        output['y_reserves'] = [
            item / (y_decimals ** 18) for item in output['y_reserves']
        ]
        output['lp_total_supply'] = [
            item / (10 ** 18) for item in output['lp_total_supply']
        ]

    return output

