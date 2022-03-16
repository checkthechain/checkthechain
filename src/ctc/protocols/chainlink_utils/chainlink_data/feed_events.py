import typing

from ctc import evm
from ctc import spec
from ctc.toolbox import pd_utils

from .. import chainlink_metadata
from .. import chainlink_spec
from . import feed_datum


async def async_get_full_feed_event_data(
    feed: chainlink_spec._FeedReference,
    start_block: typing.Optional[spec.BlockNumberReference] = None,
    end_block: typing.Optional[spec.BlockNumberReference] = None,
    normalize: bool = True,
    interpolate: bool = False,
    provider: spec.ProviderSpec = None,
    keep_multiindex: bool = False,
    invert: bool = False,
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
        verbose=False,
    )

    # rename columns
    new_columns = {
        'arg__current': 'answer',
        'arg__updatedAt': 'timestamp',
        'arg__roundId': 'round_id',
    }
    df = df.rename(columns=new_columns)
    df = df[['answer', 'timestamp', 'round_id']]

    # normalize
    if normalize:
        decimals = chainlink_metadata.get_feed_decimals(
            feed=feed, provider=provider
        )
        df['answer'] /= 10 ** decimals

    # interpolate
    if interpolate:

        if keep_multiindex:
            raise Exception('cannot use keep_multiindex and interpolate')
        df.index = pd_utils.keep_level(df.index, level='block_number')

        # add initial data
        if start_block < df.index.values[0]:
            import pandas as pd

            initial_data = await feed_datum.async_get_feed_datum(
                feed=feed,
                block=start_block,
                provider=provider,
                normalize=normalize,
                fields='full',
            )
            initial_df = pd.DataFrame(initial_data, index=[start_block])
            df = pd.concat([initial_df, df])

        end_block = await evm.async_block_number_to_int(
            end_block, provider=provider
        )
        df = pd_utils.interpolate_dataframe(df, end_index=end_block)

    elif not keep_multiindex:
        df.index = pd_utils.keep_level(df.index, level='block_number')

    if invert:
        df['answer'] = 1 / df['answer']

    return df


async def async_get_answer_feed_event_data(
    feed: chainlink_spec._FeedReference,
    start_block: typing.Optional[spec.BlockNumberReference] = None,
    end_block: typing.Optional[spec.BlockNumberReference] = None,
    normalize: bool = True,
    interpolate: bool = False,
    provider: spec.ProviderSpec = None,
    keep_multiindex: bool = False,
    invert: bool = False,
) -> spec.Series:

    df = await async_get_full_feed_event_data(
        feed=feed,
        start_block=start_block,
        end_block=end_block,
        normalize=normalize,
        interpolate=interpolate,
        provider=provider,
        keep_multiindex=keep_multiindex,
        invert=invert,
    )

    return df['answer']

