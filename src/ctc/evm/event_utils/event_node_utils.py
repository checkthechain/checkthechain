from __future__ import annotations

import typing

import toolstr

from ctc import spec
from .. import binary_utils
from .. import block_utils
from . import event_query_utils

if typing.TYPE_CHECKING:
    from typing_extensions import Literal


async def _async_query_events_from_node(
    *,
    contract_address: spec.Address | None,
    event_hash: typing.Any | None,
    topic1: typing.Any | None,
    topic2: typing.Any | None,
    topic3: typing.Any | None,
    start_block: int,
    end_block: int,
    context: spec.Context = None,
    verbose: bool | int,
    binary_output_format: Literal['binary', 'prefix_hex'] = 'binary',
    chunk_size: int = 100000,
    max_blocks_per_request: int = 2000,
) -> spec.DataFrame:
    """query events from node and cache results in db if desired"""

    import asyncio
    import polars as pl
    from ctc.toolbox import pl_utils
    from ctc.toolbox import range_utils

    # parse query type
    query_type = event_query_utils._parse_event_query_type(
        contract_address=contract_address,
        event_hash=event_hash,
        topic1=topic1,
        topic2=topic2,
        topic3=topic3,
    )
    if query_type == 8:
        raise Exception(
            'querying only by non-event-type topics is unsupported by some providers'
        )

    # break into chunks, each will be independently written to db
    chunk_ranges = range_utils.range_to_chunks(
        start=start_block,
        end=end_block,
        chunk_size=chunk_size,
    )

    if verbose >= 1:
        n_blocks = end_block - start_block + 1
        print('fetching events from node over', toolstr.format(n_blocks), 'blocks')
    if verbose >= 2:
        from ctc import cli
        from ctc import config

        event_query_utils.print_event_query_summary(
            contract_address=contract_address,
            event_hash=event_hash,
            topic1=topic1,
            topic2=topic2,
            topic3=topic3,
            start_block=start_block,
            end_block=end_block,
        )
        network = config.get_context_chain_id(context)
        cli.print_bullet(key='network', value=network)
        cli.print_bullet(key='chunk_size', value=chunk_size)
        cli.print_bullet(key='n_chunks', value=len(chunk_ranges))

    # TODO: make this async, store indirect reference in dict and pass dict
    latest_block_number = await block_utils.async_get_latest_block_number(
        context=context
    )

    # process each meta chunk
    coroutines = []
    for chunk_start, chunk_end in chunk_ranges:
        coroutine = _async_query_node_events_chunk(
            contract_address=contract_address,
            event_hash=event_hash,
            topic1=topic1,
            topic2=topic2,
            topic3=topic3,
            chunk_start=chunk_start,
            chunk_end=chunk_end,
            context=context,
            latest_block_number=latest_block_number,
            max_blocks_per_request=max_blocks_per_request,
        )
        coroutines.append(coroutine)
    chunks = await asyncio.gather(*coroutines)

    # package result in dataframe
    result = [response for chunk in chunks for response in chunk]
    columns = event_query_utils.get_event_df_columns(binary_format='prefix_hex')
    df = pl.DataFrame(result, schema=columns)

    # convert binary output columns
    if binary_output_format == 'prefix_hex':
        # already in prefix hex
        pass
    elif binary_output_format == 'binary':
        df = pl_utils.prefix_hex_columns_to_binary(
            df=df,
            columns=['topic1', 'topic2', 'topic3', 'unindexed'],
        )
    else:
        raise Exception('unknown binary_output_format')

    return df


async def _async_query_node_events_chunk(
    *,
    contract_address: spec.Address | None,
    event_hash: bytes | str | None,
    topic1: bytes | str | None,
    topic2: bytes | str | None,
    topic3: bytes | str | None,
    chunk_start: int,
    chunk_end: int,
    context: spec.Context,
    max_blocks_per_request: int = 2000,
    latest_block_number: int | None = None,
) -> typing.Sequence[spec.EncodedEvent]:
    """process a chunk of events from node"""

    import asyncio
    from ctc import config
    from ctc import rpc
    from ctc.toolbox import range_utils

    # break each meta chunk into requests
    chunk_requests = range_utils.range_to_chunks(
        start=chunk_start,
        end=chunk_end,
        chunk_size=max_blocks_per_request,
    )

    # encode topics
    if event_hash is not None:
        event_hash = binary_utils.to_hex(event_hash)
    if topic1 is not None:
        topic1 = binary_utils.to_hex(topic1)
    if topic2 is not None:
        topic2 = binary_utils.to_hex(topic2)
    if topic3 is not None:
        topic3 = binary_utils.to_hex(topic3)

    # assemble topics
    if topic3 is not None:
        topics = [event_hash, topic1, topic2, topic3]
    elif topic2 is not None:
        topics = [event_hash, topic1, topic2]
    elif topic1 is not None:
        topics = [event_hash, topic1]
    else:
        topics = [event_hash]

    # request from node
    coroutines = []
    for request_start, request_end in chunk_requests:
        coroutine = rpc.async_eth_get_logs(
            address=contract_address,
            topics=topics,
            start_block=request_start,
            end_block=request_end,
            context=context,
        )
        coroutines.append(coroutine)
    results = await asyncio.gather(*coroutines)

    # process raw events
    raw_logs = [event for result in results for event in result]
    encoded_events = [
        log[:5] + log[5] + ((None,) * (4 - len(log[5]))) + (log[6],)
        for log in raw_logs
    ]

    # write encoded events to database
    read_cache, write_cache = config.get_context_cache_read_write(
        schema_name='events', context=context
    )
    if write_cache:
        from ctc import db

        query_type = event_query_utils._parse_event_query_type(
            contract_address=contract_address,
            event_hash=event_hash,
            topic1=topic1,
            topic2=topic2,
            topic3=topic3,
        )

        query: spec.DBEventQuery = {
            'query_type': query_type,
            'contract_address': contract_address,
            'event_hash': event_hash,
            'topic1': topic1,
            'topic2': topic2,
            'topic3': topic3,
            'start_block': chunk_start,
            'end_block': chunk_end,
        }
        await db.async_intake_encoded_events(
            encoded_events=encoded_events,
            query=query,
            context=context,
            latest_block=latest_block_number,
        )

    return encoded_events


# async def _async_process_raw_node_logs(
#     raw_logs: typing.Sequence[spec.RawLog],
# ) -> typing.Sequence[spec.EncodedEvent]:
#     """convert from raw logs from node into encoded events for db"""
#     for log in raw_logs:
#         event: spec.EncodedEvent = log  # type: ignore
#         event['contract_address'] = log.pop('address')  # type: ignore
#         event['unindexed'] = log.pop('data')  # type: ignore
#         topics = log.pop('topics')  # type: ignore
#         if topics is not None and len(topics) > 0:
#             topic_iter = iter(topics)
#             if len(topics) >= 1:
#                 event['event_hash'] = next(topic_iter)
#             if len(topics) >= 2:
#                 event['topic1'] = next(topic_iter)
#             if len(topics) >= 3:
#                 event['topic2'] = next(topic_iter)
#             if len(topics) >= 4:
#                 event['topic3'] = next(topic_iter)
#     return raw_logs  # type: ignore

