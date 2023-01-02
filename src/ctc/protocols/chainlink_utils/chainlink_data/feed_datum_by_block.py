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
) -> spec.Series:
    import asyncio
    import pandas as pd
    from ctc.toolbox import pd_utils

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
    series = pd.Series(data=result, index=int_blocks)  # type: ignore

    # interpolate blocks
    if interpolate:
        series = pd_utils.interpolate_series(series=series)

    if typing.TYPE_CHECKING:
        return typing.cast(spec.Series, series)
    else:
        return series


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
    import pandas as pd
    from ctc.toolbox import pd_utils

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
    df: spec.DataFrame = pd.DataFrame(result, index=int_blocks)  # type: ignore

    # interpolate blocks
    if interpolate:
        df = pd_utils.interpolate_dataframe(df=df)

    return df

