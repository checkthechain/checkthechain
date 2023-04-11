from __future__ import annotations

import typing

from ctc import spec
from ctc import evm

from .. import chainlink_spec
from . import feed_datum


async def async_get_feed_answer_datum_by_block(
    feed: chainlink_spec._FeedReference,
    blocks: typing.Sequence[spec.BlockNumberReference],
    *,
    context: spec.Context = None,
    normalize: bool = True,
    interpolate: bool = True,
    invert: bool = False,
) -> spec.DataFrame:
    import asyncio
    from ctc.toolbox import pl_utils
    import polars as pl

    int_blocks = await evm.async_block_numbers_to_int(
        blocks=blocks, context=context
    )

    # query data
    coroutines = []
    for block in int_blocks:
        coroutine = feed_datum.async_get_feed_datum(
            feed=feed,
            fields='answer',
            normalize=normalize,
            block=block,
            invert=invert,
            context=context,
        )
        coroutines.append(coroutine)
    result = await asyncio.gather(*coroutines)

    # create series
    df = pl.DataFrame({'block_number': int_blocks, 'answer': result})

    # interpolate blocks
    if interpolate:
        df = pl_utils.interpolate(df, index_column='block_number')

    return df


async def async_get_feed_full_datum_by_block(
    feed: chainlink_spec._FeedReference,
    blocks: typing.Sequence[spec.BlockNumberReference],
    *,
    context: spec.Context = None,
    normalize: bool = True,
    interpolate: bool = True,
    invert: bool = False,
) -> spec.DataFrame:
    import asyncio
    import polars as pl
    from ctc.toolbox import pl_utils

    int_blocks = await evm.async_block_numbers_to_int(
        blocks=blocks, context=context
    )

    # query data
    coroutines = []
    for block in int_blocks:
        coroutine = feed_datum.async_get_feed_datum(
            feed=feed,
            block=block,
            normalize=normalize,
            fields='full',
            invert=invert,
            context=context,
        )
        coroutines.append(coroutine)
    result = await asyncio.gather(*coroutines)

    # create series
    df = pl.DataFrame({'block_number': int_blocks, 'answer': result})

    # interpolate blocks
    if interpolate:
        df = pl_utils.interpolate(df, index_column='block_number')

    return df

