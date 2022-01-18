import typing

from ctc import evm
from ctc import spec
from ctc.toolbox import pd_utils

from .. import chainlink_metadata
from .. import chainlink_spec


async def async_get_full_feed_event_data(
    feed: chainlink_spec._FeedReference,
    start_block: typing.Optional[spec.BlockNumberReference] = None,
    end_block: typing.Optional[spec.BlockNumberReference] = None,
    normalize: bool = True,
    interpolate: bool = False,
    provider: spec.ProviderSpec = None,
) -> spec.DataFrame:
    """
    TODO: be able to gather data across multiple aggregator changes
    """

    # get feed address
    feed = await chainlink_metadata.async_resolve_feed_address(
        feed, provider=provider
    )

    # get aggregator
    if end_block is None:
        end_block = await evm.async_get_latest_block_number()
    aggregator_address = await chainlink_metadata.async_get_feed_aggregator(
        feed=feed,
        block=end_block,
        provider=provider,
    )

    # get events
    df = await evm.async_get_events(
        contract_address=aggregator_address,
        event_name='AnswerUpdated',
        start_block=start_block,
        end_block=end_block,
    )

    # normalize
    if normalize:
        decimals = chainlink_metadata.get_feed_decimals(
            feed=feed, provider=provider
        )
        df['answer'] /= 10 ** decimals

    # interpolate
    if interpolate:
        df = pd_utils.interpolate_dataframe(df, level='block_number')

    return df


async def async_get_answer_feed_event_data(
    feed: chainlink_spec._FeedReference,
    start_block: typing.Optional[spec.BlockNumberReference] = None,
    end_block: typing.Optional[spec.BlockNumberReference] = None,
    normalize: bool = True,
    interpolate: bool = False,
    provider: spec.ProviderSpec = None,
) -> spec.Series:

    df = await async_get_full_feed_event_data(
        feed=feed,
        start_block=start_block,
        end_block=end_block,
        normalize=normalize,
        interpolate=interpolate,
        provider=provider,
    )

    return df['answer']

