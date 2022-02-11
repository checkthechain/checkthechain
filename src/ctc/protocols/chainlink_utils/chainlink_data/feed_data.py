from __future__ import annotations

import typing

from ctc import spec

from .. import chainlink_metadata
from .. import chainlink_spec
from . import feed_datum_by_block
from . import feed_events


@typing.overload
async def async_get_feed_data(
    feed: chainlink_spec._FeedReference,
    *,
    fields: typing.Literal['full'],
    blocks: typing.Sequence[spec.BlockNumberReference] = None,
    start_block: typing.Optional[spec.BlockNumberReference] = None,
    end_block: typing.Optional[spec.BlockNumberReference] = None,
    normalize: bool = True,
    interpolate: bool = False,
    provider: spec.ProviderSpec = None,
) -> spec.DataFrame:
    ...


@typing.overload
async def async_get_feed_data(
    feed: chainlink_spec._FeedReference,
    *,
    fields: typing.Literal['answer'] = 'answer',
    blocks: typing.Sequence[spec.BlockNumberReference] = None,
    start_block: typing.Optional[spec.BlockNumberReference] = None,
    end_block: typing.Optional[spec.BlockNumberReference] = None,
    normalize: bool = True,
    interpolate: bool = False,
    provider: spec.ProviderSpec = None,
) -> spec.Series:
    ...


async def async_get_feed_data(
    feed: chainlink_spec._FeedReference,
    *,
    fields: typing.Literal['answer', 'full'] = 'answer',
    blocks: typing.Sequence[spec.BlockNumberReference] = None,
    start_block: typing.Optional[spec.BlockNumberReference] = None,
    end_block: typing.Optional[spec.BlockNumberReference] = None,
    normalize: bool = True,
    interpolate: bool = False,
    provider: spec.ProviderSpec = None,
) -> typing.Union[spec.DataFrame, spec.Series]:

    # determine blocks
    if (blocks is not None) and [start_block, end_block].count(None) < 2:
        raise Exception('should only provide one block specification')
    if blocks is None:
        if start_block is None:
            start_block = await chainlink_metadata.async_get_feed_first_block(
                feed=feed,
                provider=provider,
            )
        if end_block is None:
            end_block = 'latest'

    # perform query
    if fields == 'answer':

        if blocks is not None:
            return (
                await feed_datum_by_block.async_get_feed_answer_datum_by_block(
                    feed,
                    provider=provider,
                    blocks=blocks,
                    normalize=normalize,
                    interpolate=interpolate,
                )
            )

        else:
            return await feed_events.async_get_answer_feed_event_data(
                feed,
                provider=provider,
                normalize=normalize,
                start_block=start_block,
                end_block=end_block,
                interpolate=interpolate,
            )

    elif fields == 'full':

        if blocks is not None:
            return await feed_datum_by_block.async_get_feed_full_datum_by_block(
                feed,
                provider=provider,
                blocks=blocks,
                normalize=normalize,
                interpolate=interpolate,
            )

        else:
            return await feed_events.async_get_full_feed_event_data(
                feed,
                provider=provider,
                normalize=normalize,
                start_block=start_block,
                end_block=end_block,
                interpolate=interpolate,
            )

    else:
        raise Exception('unknown fields format: ' + str(fields))

