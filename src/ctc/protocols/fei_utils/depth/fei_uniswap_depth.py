from __future__ import annotations

import asyncio
import typing

from ctc import directory
from ctc.protocols import uniswap_v3_utils


async def async_get_fei_uniswap_pools() -> list[list[typing.Any]]:
    # TODO: automate

    FEI = directory.get_erc20_address('FEI')
    DAI = directory.get_erc20_address('DAI')
    USDC = directory.get_erc20_address('USDC')

    # token_in, token_out, fee
    pools = [
        [FEI, DAI, 500, 18, 18],
        [FEI, USDC, 100, 18, 6],
        [FEI, USDC, 500, 18, 6],
    ]

    return pools


async def async_get_fei_uniswap_pool_price_depth(
    pools: list[list[typing.Any]] | None = None, prices: typing.Sequence[float] | None = None
) -> dict[str, dict[float, float]]:
    if pools is None:
        pools = await async_get_fei_uniswap_pools()

    if prices is None:
        prices = [
            0.995,
            0.993,
            0.990,
        ]

    coroutines = {}
    for price_level in prices:
        for p in range(len(pools)):
            (
                token_in,
                token_out,
                fee,
                token_in_decimals,
                token_out_decimals,
            ) = pools[p]
            swap_kwargs = {
                'token_in': token_in,
                'token_out': token_out,
                'fee': fee,
                'token_in_decimals': token_in_decimals,
                'token_out_decimals': token_out_decimals,
            }

            coroutines[
                (p, price_level)
            ] = uniswap_v3_utils.async_get_liquidity_depth(
                new_price=price_level,
                **swap_kwargs,
            )

    depths = await asyncio.gather(*coroutines.values())

    pool_price_depth: dict[str, dict[float, float]] = {}
    for (p, price_level), depth in zip(coroutines.keys(), depths):
        token_in, token_out, fee, token_in_decimals, token_out_decimals = pools[
            p
        ]

        symbol_in = directory.get_erc20_metadata(address=token_in)['symbol']
        symbol_out = directory.get_erc20_metadata(address=token_out)['symbol']
        pool = (
            'Uniswap V3 '
            + symbol_in
            + '_'
            + symbol_out
            + ' '
            + ('%.2d' % (fee / 100))
        )

        pool_price_depth.setdefault(pool, {})
        pool_price_depth[pool][price_level] = depth

    return pool_price_depth

