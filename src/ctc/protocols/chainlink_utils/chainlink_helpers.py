import typing

from ctc import spec

from . import chainlink_data


async def async_get_eth_price(
    block: spec.BlockNumberReference = 'latest',
    provider: spec.ProviderSpec = None,
    normalize: bool = True,
):
    return await chainlink_data.async_get_feed_datum(
        feed='ETH_USD',
        normalize=normalize,
        provider=provider,
        block=block,
    )


async def async_get_eth_price_by_block(
    blocks: typing.Sequence[spec.BlockNumberReference],
    provider: spec.ProviderSpec = None,
    normalize: bool = True,
):
    return await chainlink_data.async_get_feed_data(
        feed='ETH_USD',
        normalize=normalize,
        provider=provider,
        blocks=blocks,
    )

