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
    import polars as pl


async def async_get_full_feed_event_data(
    feed: chainlink_spec._FeedReference,
    *,
    start_block: typing.Optional[spec.BlockNumberReference] = None,
    end_block: typing.Optional[spec.BlockNumberReference] = None,
    start_time: tooltime.Timestamp | None = None,
    end_time: tooltime.Timestamp | None = None,
    normalize: bool = True,
    interpolate: bool = False,
    context: spec.Context = None,
    invert: bool = False,
) -> spec.DataFrame:
    """
    TODO: be able to gather data across multiple aggregator changes
    """

    from ctc.toolbox import pl_utils
    import polars as pl

    # get feed address
    feed = await chainlink_feed_metadata.async_resolve_feed_address(
        feed, context=context
    )

    # get aggregator
    start_block, end_block = await evm.async_resolve_block_range(
        start_block=start_block,
        end_block=end_block,
        start_time=start_time,
        end_time=end_time,
        allow_none=True,
        context=context,
    )
    if start_block is None:
        start_block = await chainlink_feed_metadata.async_get_feed_first_block(
            feed=feed,
            context=context,
        )
    if end_block is None:
        end_block = await evm.async_get_latest_block_number(context=context)
    aggregator_address = (
        await chainlink_feed_metadata.async_get_feed_aggregator(
            feed=feed,
            block=end_block,
            context=context,
        )
    )

    # check if dealing with multiple aggregators
    initial_aggregator_address = (
        await chainlink_feed_metadata.async_get_feed_aggregator(
            feed=feed,
            block=start_block,
            context=context,
        )
    )
    if aggregator_address != initial_aggregator_address:
        history = await chainlink_aggregators.async_get_feed_aggregator_history(
            feed=feed,
            context=context,
        )
        aggregator_starts = list(history.values())
        aggregator_ends = [block - 1 for block in aggregator_starts[1:]]
        start_block = await evm.async_block_number_to_int(
            start_block, context=context
        )
        end_block = await evm.async_block_number_to_int(
            end_block, context=context
        )
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
                context=context,
                integer_output_format={'updatedAt': int},
            )
            coroutines.append(coroutine)
        results = await asyncio.gather(*coroutines)

        # currently need this check as empty results do not have arg columns
        non_empty_results = [result for result in results if len(result) > 0]
        if len(non_empty_results) == 0:
            df: spec.DataFrame = results[0]
        else:
            df = pl_utils.concat(non_empty_results)

    else:

        df = await evm.async_get_events(
            contract_address=aggregator_address,
            event_abi=chainlink_spec.aggregator_event_abis['AnswerUpdated'],
            start_block=start_block,
            end_block=end_block,
            verbose=False,
            context=context,
            integer_output_format={'updatedAt': pl.Int64},
        )

    # rename columns
    new_columns = {
        'arg__current': 'answer',
        'arg__updatedAt': 'timestamp',
        'arg__roundId': 'round_id',
    }
    df = df.rename(new_columns)
    df = df[['block_number', 'answer', 'timestamp', 'round_id']]

    # normalize
    if normalize:
        import numpy as np

        decimals = await chainlink_feed_metadata.async_get_feed_decimals(
            feed=feed, context=context
        )
        df = df.with_columns(
            pl.Series(
                'answer',
                np.array(df['answer'].to_list(), dtype=float) / (10**decimals),
            )
        )

    # interpolate
    if interpolate:

        # TODO: better detection of initial feed data point
        first_feed_block = (
            await chainlink_feed_metadata.async_get_feed_first_block(
                feed, context=context
            )
        )
        if start_block == first_feed_block:
            pass
        else:

            # add initial data
            if len(df) == 0 or start_block < df['block_number'][0]:
                initial_data = await feed_datum.async_get_feed_datum(
                    feed=feed,
                    block=start_block,
                    normalize=normalize,
                    fields='full',
                    context=context,
                )
                schema = {
                    'block_number': pl.Int64,
                    'timestamp': pl.Int64,
                    'round_id': pl.Object,
                }
                if normalize:
                    schema['answer'] = pl.Float64
                else:
                    schema['answer'] = pl.Decimal
                initial_data['block_number'] = start_block
                initial_df = pl.DataFrame(initial_data, schema=schema)
                df = pl_utils.concat([initial_df, df])

        end_block = await evm.async_block_number_to_int(
            end_block, context=context
        )
        df = pl_utils.interpolate(
            df, index_column='block_number', end_index=end_block
        )

    if invert:
        df = df.with_columns(1 / df['answer'])

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
    invert: bool = False,
    context: spec.Context = None,
) -> spec.DataFrame:

    from ctc.toolbox import pl_utils

    df = await async_get_full_feed_event_data(
        feed=feed,
        start_block=start_block,
        end_block=end_block,
        start_time=start_time,
        end_time=end_time,
        normalize=normalize,
        interpolate=interpolate,
        context=context,
        invert=invert,
    )

    output = df[['block_number', 'answer']]

    return output

