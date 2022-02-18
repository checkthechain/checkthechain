import asyncio

from ctc import rpc
from ctc.protocols import chainlink_utils

from . import aave_spec


async def async_get_asset_price(
    asset,
    provider=None,
    block='latest',
    normalize=True,
    units='usd',
):

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
    asset, blocks, provider=None, normalize=True, units='usd',
):
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

