import asyncio
import typing

import pandas as pd

from ctc import spec
from ctc import evm
from ctc.toolbox import pd_utils

from .. import chainlink_spec
from . import feed_datum


async def async_get_feed_answer_datum_by_block(
    feed: chainlink_spec._FeedReference,
    blocks: typing.Sequence[spec.BlockNumberReference],
    provider: spec.ProviderSpec = None,
    normalize: bool = True,
    interpolate: bool = True,
) -> spec.Series:

    int_blocks = await evm.async_block_numbers_to_int(blocks=blocks)

    # query data
    coroutines = []
    for block in int_blocks:
        coroutine = feed_datum.async_get_feed_datum(
            feed=feed,
            fields='answer',
            normalize=normalize,
            block=block,
            provider=provider,
        )
        coroutines.append(coroutine)
    result = await asyncio.gather(*coroutines)

    # create series
    series = pd.Series(data=result, index=int_blocks)

    # interpolate blocks
    if interpolate:
        series = pd_utils.interpolate_series(series=series)

    return series


async def async_get_feed_full_datum_by_block(
    feed: chainlink_spec._FeedReference,
    blocks: typing.Sequence[spec.BlockNumberReference],
    provider: spec.ProviderSpec = None,
    normalize: bool = True,
    interpolate: bool = True,
) -> spec.DataFrame:

    int_blocks = await evm.async_block_numbers_to_int(blocks=blocks)

    # query data
    coroutines = []
    for block in int_blocks:
        coroutine = feed_datum.async_get_feed_datum(
            feed=feed,
            block=block,
            provider=provider,
            normalize=normalize,
            fields='full',
        )
        coroutines.append(coroutine)
    result = await asyncio.gather(*coroutines)

    # create series
    df = pd.DataFrame(result, index=int_blocks)

    # interpolate blocks
    if interpolate:
        df = pd_utils.interpolate_dataframe(df=df)

    return df

