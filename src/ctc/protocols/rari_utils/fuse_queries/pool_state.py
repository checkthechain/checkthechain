from __future__ import annotations

import typing

from ctc.protocols import chainlink_utils
from ctc import spec

from . import pool_metadata
from . import token_state


async def async_get_pool_prices(
    *,
    oracle: spec.Address | None = None,
    ctokens: typing.Sequence[spec.Address] | None = None,
    comptroller: spec.Address | None = None,
    block: spec.BlockNumberReference = 'latest',
    to_usd: bool = True,
) -> dict[spec.Address, spec.Number]:
    import asyncio

    if oracle is None:
        if comptroller is None:
            raise Exception('specify comptroller')
        oracle = await pool_metadata.async_get_pool_oracle(
            comptroller, block=block
        )
    if ctokens is None:
        if comptroller is None:
            raise Exception('specify comptroller')
        ctokens = await pool_metadata.async_get_pool_ctokens(
            comptroller, block=block
        )

    coroutines = [
        token_state.async_get_ctoken_price(
            ctoken=ctoken, oracle=oracle, block=block
        )
        for ctoken in ctokens
    ]
    prices = await asyncio.gather(*coroutines)

    if to_usd:
        eth_price = await chainlink_utils.async_get_eth_price(block=block)
        prices = [price * eth_price for price in prices]

    return dict(zip(ctokens, prices))


async def async_get_pool_tvl_and_tvb(
    *,
    comptroller: spec.Address | None = None,
    ctokens: typing.Sequence[spec.Address] | None = None,
    oracle: spec.Address | None = None,
    block: spec.BlockNumberReference = 'latest',
) -> dict[str, spec.Number]:

    import asyncio

    if ctokens is None:
        if comptroller is None:
            raise Exception(
                'must specify comptroller if not specifying ctokens'
            )
        ctokens = await pool_metadata.async_get_pool_ctokens(
            comptroller=comptroller, block=block
        )
    if oracle is None:
        if comptroller is None:
            raise Exception('must specify comptroller if not specifying oracle')
        oracle = await pool_metadata.async_get_pool_oracle(
            comptroller=comptroller, block=block
        )

    eth_price = await chainlink_utils.async_get_eth_price(block=block)

    ctokens_stats_coroutine = [
        asyncio.create_task(
            token_state.async_get_ctoken_tvl_and_tvb(
                ctoken, oracle=oracle, eth_price=eth_price, block=block
            )
        )
        for ctoken in ctokens
    ]
    ctokens_stats = await asyncio.gather(*ctokens_stats_coroutine)

    tvl = 0
    tvb = 0
    for ctoken_stats in ctokens_stats:
        tvl += ctoken_stats['tvl']
        tvb += ctoken_stats['tvb']

    return {'tvl': tvl, 'tvb': tvb}
