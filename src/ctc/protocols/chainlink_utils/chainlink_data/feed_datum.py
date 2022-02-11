from __future__ import annotations

import typing

from ctc import rpc
from ctc import spec

from .. import chainlink_metadata
from .. import chainlink_spec


@typing.overload
async def async_get_feed_datum(
    feed: chainlink_spec._FeedReference,
    *,
    fields: typing.Literal['full'],
    normalize: typing.Literal[False],
    block: typing.Optional[spec.BlockNumberReference] = None,
    provider: spec.ProviderSpec = None,
) -> chainlink_spec.FeedRoundData:
    ...


@typing.overload
async def async_get_feed_datum(
    feed: chainlink_spec._FeedReference,
    *,
    fields: typing.Literal['full'],
    normalize: typing.Literal[True],
    block: typing.Optional[spec.BlockNumberReference] = None,
    provider: spec.ProviderSpec = None,
) -> chainlink_spec.FeedRoundDataNormalized:
    ...


# overloading in python is a mess...
@typing.overload
async def async_get_feed_datum(
    feed: chainlink_spec._FeedReference,
    *,
    fields: typing.Literal['full'],
    normalize: bool = True,
    block: typing.Optional[spec.BlockNumberReference] = None,
    provider: spec.ProviderSpec = None,
) -> typing.Union[
    chainlink_spec.FeedRoundData, chainlink_spec.FeedRoundDataNormalized
]:
    ...


@typing.overload
async def async_get_feed_datum(
    feed: chainlink_spec._FeedReference,
    *,
    fields: typing.Literal['answer'] = 'answer',
    normalize: typing.Literal[False],
    block: typing.Optional[spec.BlockNumberReference] = None,
    provider: spec.ProviderSpec = None,
) -> int:
    ...


@typing.overload
async def async_get_feed_datum(
    feed: chainlink_spec._FeedReference,
    *,
    fields: typing.Literal['answer'] = 'answer',
    normalize: bool = True,
    block: typing.Optional[spec.BlockNumberReference] = None,
    provider: spec.ProviderSpec = None,
) -> float:
    ...


async def async_get_feed_datum(
    feed: chainlink_spec._FeedReference,
    *,
    fields: typing.Literal['answer', 'full'] = 'answer',
    normalize: bool = True,
    block: typing.Optional[spec.BlockNumberReference] = None,
    provider: spec.ProviderSpec = None,
) -> typing.Union[
    int,
    float,
    chainlink_spec.FeedRoundData,
    chainlink_spec.FeedRoundDataNormalized,
]:
    """get feed data for a single block"""

    if block is None:
        block = 'latest'

    feed = await chainlink_metadata.async_resolve_feed_address(feed)

    if fields == 'answer':

        answer = await rpc.async_eth_call(
            to_address=feed,
            function_name='latestAnswer',
            block_number=block,
            provider=provider,
            fill_empty=True,
            empty_token=None,
        )

        if normalize and answer is not None:
            decimals = chainlink_metadata.get_feed_decimals(feed)
            answer /= 10 ** decimals

        return answer

    elif fields == 'full':

        data = await rpc.async_eth_call(
            to_address=feed,
            function_name='latestRoundData',
            block_number=block,
            provider=provider,
            fill_empty=True,
            empty_token=None,
        )

        round_id, answer, _started_at, updated_at, _answered_in_round_id = data

        full: chainlink_spec.FeedRoundData = {
            'answer': answer,
            'timestamp': updated_at,
            'round_id': round_id,
        }

        if normalize and answer is not None:
            decimals = chainlink_metadata.get_feed_decimals(feed)
            full['answer'] /= 10 ** decimals
            return full

        else:

            return full

    else:
        raise Exception('unknown fields type: ' + str(fields))

