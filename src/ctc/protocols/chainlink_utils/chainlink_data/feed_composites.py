from __future__ import annotations

import typing

from ctc import evm
from ctc import spec
from .. import chainlink_spec
from .. import chainlink_feed_metadata
from . import feed_data

if typing.TYPE_CHECKING:
    import tooltime


async def async_get_composite_feed_data(
    composite_feed: typing.Sequence[chainlink_spec._FeedReference],
    *,
    start_block: typing.Optional[spec.BlockNumberReference] = None,
    end_block: typing.Optional[spec.BlockNumberReference] = None,
    start_time: tooltime.Timestamp | None = None,
    end_time: tooltime.Timestamp | None = None,
    invert: bool = False,
    provider: spec.ProviderReference = None,
) -> spec.Series:
    # TODO: other ways of specifying composites
    import asyncio

    start_block, end_block = await evm.async_resolve_block_range(
        start_block=start_block,
        end_block=end_block,
        start_time=start_time,
        end_time=end_time,
        allow_none=True,
        provider=provider,
    )

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

    datas: typing.Sequence[spec.Series] = await asyncio.gather(*coroutines)

    # compute product
    product = datas[0] * datas[1]
    for data in datas[2:]:
        product = product * data

    # normalize
    feeds_decimals_coroutines = [
        chainlink_feed_metadata.async_get_feed_decimals(
            feed=feed,
            provider=provider,
        )
        for feed in composite_feed
    ]
    feeds_decimals = await asyncio.gather(*feeds_decimals_coroutines)
    composite_decimals = sum(feeds_decimals)
    product = product / (10 ** composite_decimals)

    # invert
    if invert:
        product = 1 / product

    return product
