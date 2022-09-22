from __future__ import annotations

import asyncio
import typing

from ctc import evm
from ctc import spec

from .. import chainlink_aggregators
from .. import chainlink_feed_metadata
from .. import chainlink_spec
from . import feed_datum

if typing.TYPE_CHECKING:
    import tooltime


async def async_get_full_feed_event_data(
    feed: chainlink_spec._FeedReference,
    *,
    start_block: typing.Optional[spec.BlockNumberReference] = None,
    end_block: typing.Optional[spec.BlockNumberReference] = None,
    start_time: tooltime.Timestamp | None = None,
    end_time: tooltime.Timestamp | None = None,
    normalize: bool = True,
    interpolate: bool = False,
    provider: spec.ProviderReference = None,
    keep_multiindex: bool = False,
    invert: bool = False,
) -> spec.DataFrame:
    """
    TODO: be able to gather data across multiple aggregator changes
    """
    import pandas as pd
    from ctc.toolbox import pd_utils

    # get feed address
    feed = await chainlink_feed_metadata.async_resolve_feed_address(
        feed, provider=provider
    )

    # get aggregator
    start_block, end_block = await evm.async_resolve_block_range(
        start_block=start_block,
        end_block=end_block,
        start_time=start_time,
        end_time=end_time,
        allow_none=True,
        provider=provider,
    )
    if start_block is None:
        start_block = await chainlink_feed_metadata.async_get_feed_first_block(
            feed=feed,
            provider=provider,
        )
    if end_block is None:
        end_block = await evm.async_get_latest_block_number()
    aggregator_address = (
        await chainlink_feed_metadata.async_get_feed_aggregator(
            feed=feed,
            block=end_block,
            provider=provider,
        )
    )

    # check if dealing with multiple aggregators
    initial_aggregator_address = (
        await chainlink_feed_metadata.async_get_feed_aggregator(
            feed=feed,
            block=start_block,
            provider=provider,
        )
    )
    if aggregator_address != initial_aggregator_address:
        history = await chainlink_aggregators.async_get_feed_aggregator_history(
            feed=feed,
            provider=provider,
        )
        aggregator_starts = list(history.values())
        aggregator_ends = [block - 1 for block in aggregator_starts[1:]]
        start_block = await evm.async_block_number_to_int(start_block)
        end_block = await evm.async_block_number_to_int(end_block)
        aggregator_ends.append(end_block)
        coroutines = []
        for aggregator, aggregator_start, aggregator_end in zip(
            history.keys(), aggregator_starts, aggregator_ends
        ):
            if aggregator_start < start_block:
                use_start = start_block
            else:
                use_start = aggregator_start

            if aggregator_end > end_block:
                use_end = end_block
            else:
                use_end = aggregator_end

            if aggregator_start > aggregator_end:
                continue

            coroutine = evm.async_get_events(
                contract_address=aggregator,
                event_abi=chainlink_spec.aggregator_event_abis['AnswerUpdated'],
                start_block=use_start,
                end_block=use_end,
                verbose=False,
            )
            coroutines.append(coroutine)
        results = await asyncio.gather(*coroutines)
        df: spec.DataFrame = pd.concat(results)

    else:
        df = await evm.async_get_events(
            contract_address=aggregator_address,
            event_abi=chainlink_spec.aggregator_event_abis['AnswerUpdated'],
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
        decimals = await chainlink_feed_metadata.async_get_feed_decimals(
            feed=feed, provider=provider
        )
        df['answer'] /= 10**decimals

    # interpolate
    if interpolate:

        if keep_multiindex:
            raise Exception('cannot use keep_multiindex and interpolate')
        df.index = pd_utils.keep_level(df.index, level='block_number')

        # TODO: better detection of initial feed data point
        first_feed_block = (
            await chainlink_feed_metadata.async_get_feed_first_block(feed)
        )
        if start_block == first_feed_block:
            pass
        else:

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
    *,
    start_block: typing.Optional[spec.BlockNumberReference] = None,
    end_block: typing.Optional[spec.BlockNumberReference] = None,
    start_time: tooltime.Timestamp | None = None,
    end_time: tooltime.Timestamp | None = None,
    normalize: bool = True,
    interpolate: bool = False,
    provider: spec.ProviderReference = None,
    keep_multiindex: bool = False,
    invert: bool = False,
) -> spec.Series:

    df = await async_get_full_feed_event_data(
        feed=feed,
        start_block=start_block,
        end_block=end_block,
        start_time=start_time,
        end_time=end_time,
        normalize=normalize,
        interpolate=interpolate,
        provider=provider,
        keep_multiindex=keep_multiindex,
        invert=invert,
    )

    return df['answer']
