from __future__ import annotations

import asyncio
import typing

from ctc import spec
from .. import chainlink_spec
from .. import chainlink_metadata
from . import feed_data


async def async_get_composite_feed_data(
    composite_feed: typing.Sequence[chainlink_spec._FeedReference],
    start_block: typing.Optional[spec.BlockNumberReference] = None,
    end_block: typing.Optional[spec.BlockNumberReference] = None,
    invert: bool = False,
    provider: spec.ProviderSpec = None,
) -> spec.Series:
    # TODO: other ways of specifying composites

    # queue requests
    coroutines = []
    for feed in composite_feed:
        coroutine = feed_data.async_get_feed_data(
            feed,
            start_block=start_block,
            end_block=end_block,
            normalize=False,
            invert=False,
            interpolate=True,
            fields='answer',
        )
        coroutines.append(coroutine)

    datas = await asyncio.gather(*coroutines)

    # compute product
    product = datas[0] * datas[1]
    for data in datas[2:]:
        product = product * data

    # normalize
    feeds_decimals = [
        chainlink_metadata.get_feed_decimals(feed=feed, provider=provider)
        for feed in composite_feed
    ]
    composite_decimals = sum(feeds_decimals)
    product = product / (10 ** composite_decimals)

    # invert
    if invert:
        product = 1 / product

    return product

