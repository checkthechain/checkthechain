from __future__ import annotations

import asyncio
import typing

from ctc.protocols import chainlink_utils
from ctc import rpc
from ctc import spec

from . import aave_spec


async def async_get_asset_price(
    asset: spec.Address,
    provider: spec.ProviderReference = None,
    block: spec.BlockNumberReference = 'latest',
    normalize: bool = True,
    units: typing.Literal['usd', 'eth'] = 'usd',
) -> typing.Sequence[int | float]:

    provider = rpc.get_provider(provider)
    network = provider['network']
    if network is None:
        raise Exception('could not determine network')

    oracle = aave_spec.get_aave_address('PriceOracle', network=network)
    price_coroutine = rpc.async_eth_call(
        to_address=oracle,
        provider=provider,
        block_number=block,
        function_name='getAssetPrice',
        function_parameters=[asset],
    )

    if units == 'eth':
        price = await price_coroutine

    elif units == 'usd':
        eth_usd_coroutine = chainlink_utils.async_get_eth_price(
            block=block, normalize=True
        )
        asset_price, eth_usd = await asyncio.gather(
            price_coroutine, eth_usd_coroutine
        )
        price = asset_price * eth_usd

    else:
        raise Exception('unknown units: ' + str(units))

    if normalize:
        price = price / 1e18

    return price


async def async_get_asset_price_by_block(
    asset: spec.Address,
    blocks: typing.Sequence[spec.BlockNumberReference],
    provider: spec.ProviderReference = None,
    normalize: bool = True,
    units: typing.Literal['usd', 'eth'] = 'usd',
) -> typing.Sequence[int | float]:
    coroutines = [
        async_get_asset_price(
            asset=asset,
            provider=provider,
            block=block,
            normalize=normalize,
            units=units,
        )
        for block in blocks
    ]
    return await asyncio.gather(*coroutines)

