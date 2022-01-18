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
    block: spec.BlockNumberReference = 'latest',
    provider: spec.ProviderSpec = None,
) -> chainlink_spec.FeedRoundData:
    ...


@typing.overload
async def async_get_feed_datum(
    feed: chainlink_spec._FeedReference,
    *,
    fields: typing.Literal['full'],
    normalize: bool = True,
    block: spec.BlockNumberReference = 'latest',
    provider: spec.ProviderSpec = None,
) -> chainlink_spec.FeedRoundDataNormalized:
    ...


@typing.overload
async def async_get_feed_datum(
    feed: chainlink_spec._FeedReference,
    *,
    fields: typing.Literal['answer'] = 'answer',
    normalize: typing.Literal[False],
    block: spec.BlockNumberReference = 'latest',
    provider: spec.ProviderSpec = None,
) -> int:
    ...


@typing.overload
async def async_get_feed_datum(
    feed: chainlink_spec._FeedReference,
    *,
    fields: typing.Literal['answer'] = 'answer',
    normalize: bool = True,
    block: spec.BlockNumberReference = 'latest',
    provider: spec.ProviderSpec = None,
) -> float:
    ...


async def async_get_feed_datum(
    feed: chainlink_spec._FeedReference,
    *,
    block: spec.BlockNumberReference = 'latest',
    provider: spec.ProviderSpec = None,
    normalize: bool = True,
    fields: typing.Literal['answer', 'full'] = 'answer',
) -> typing.Union[
    int,
    float,
    chainlink_spec.FeedRoundData,
    chainlink_spec.FeedRoundDataNormalized,
]:
    """get feed data for a single block"""

    feed = await chainlink_metadata.async_resolve_feed_address(feed)

    if fields == 'answer':

        answer = await rpc.async_eth_call(
            to_address=feed,
            function_name='latestAnswer',
            block_number=block,
            provider=provider,
        )

        if normalize:
            decimals = chainlink_metadata.get_feed_decimals(feed)
            answer /= 10 ** decimals

        return answer

    elif fields == 'full':

        full = await rpc.async_eth_call(
            to_address=feed,
            function_name='latestRoundData',
            block_number=block,
            provider=provider,
        )

        if normalize:
            decimals = chainlink_metadata.get_feed_decimals(feed)
            full['answer'] /= 10 ** decimals

        return full

    else:
        raise Exception('unknown fields type: ' + str(fields))

