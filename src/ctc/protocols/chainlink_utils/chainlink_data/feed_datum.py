from __future__ import annotations

import typing

from ctc import rpc
from ctc import spec

from .. import chainlink_feed_metadata
from .. import chainlink_spec


# overloading in python is a mess...
@typing.overload
async def async_get_feed_datum(
    feed: chainlink_spec._FeedReference,
    *,
    fields: typing.Literal['full'],
    normalize: bool = True,
    invert: bool = False,
    block: typing.Optional[spec.BlockNumberReference] = None,
    provider: spec.ProviderReference = None,
) -> chainlink_spec.FeedRoundData:
    ...


@typing.overload
async def async_get_feed_datum(
    feed: chainlink_spec._FeedReference,
    *,
    fields: typing.Literal['answer'] = 'answer',
    normalize: bool = True,
    invert: bool = False,
    block: typing.Optional[spec.BlockNumberReference] = None,
    provider: spec.ProviderReference = None,
) -> typing.Union[int, float]:
    ...


async def async_get_feed_datum(
    feed: chainlink_spec._FeedReference,
    *,
    fields: typing.Literal['answer', 'full'] = 'answer',
    normalize: bool = True,
    invert: bool = False,
    block: typing.Optional[spec.BlockNumberReference] = None,
    provider: spec.ProviderReference = None,
) -> typing.Union[int, float, chainlink_spec.FeedRoundData]:
    """get feed data for a single block"""

    if block is None:
        block = 'latest'

    feed = await chainlink_feed_metadata.async_resolve_feed_address(feed)

    if fields == 'answer':

        result = await rpc.async_eth_call(
            to_address=feed,
            function_abi=chainlink_spec.feed_function_abis['latestAnswer'],
            block_number=block,
            provider=provider,
            fill_empty=True,
            empty_token=None,
        )

        if not isinstance(result, (int, float)):
            raise Exception('invalid rpc result')
        answer = result

        if normalize:
            decimals = await chainlink_feed_metadata.async_get_feed_decimals(
                feed
            )
            answer /= 10 ** decimals

        if invert:
            answer = 1 / answer

        return answer

    elif fields == 'full':

        data = await rpc.async_eth_call(
            to_address=feed,
            function_abi=chainlink_spec.feed_function_abis['latestRoundData'],
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

        if answer is not None:
            if normalize:
                decimals = (
                    await chainlink_feed_metadata.async_get_feed_decimals(feed)
                )
                full['answer'] /= 10 ** decimals

            if invert:
                full['answer'] = 1 / full['answer']

            return full

        else:

            return full

    else:
        raise Exception('unknown fields type: ' + str(fields))
