from __future__ import annotations

import asyncio
import typing

from ctc import rpc
from ctc import spec


if typing.TYPE_CHECKING:
    T = typing.TypeVar('T', typing.Sequence[spec.RawLog], spec.DataFrame)


async def _async_query_events_from_node(
    *,
    contract_address: spec.Address | None,
    topics: typing.Sequence[typing.Any] | None,
    start_block: int,
    end_block: int,
    write_to_db: bool,
    provider: spec.ProviderReference,
) -> spec.DataFrame:
    """query events from node and cache results in db if desired"""

    import pandas as pd
    from ctc.toolbox import chunk_utils

    # break into chunks, each will be independently written to db
    chunk_size = 100000
    chunk_ranges = chunk_utils.range_to_chunks(
        start_block,
        end_block,
        chunk_size,
    )

    # process each meta chunk
    network = rpc.get_provider_network(provider)
    coroutines = []
    for chunk_range in chunk_ranges:
        coroutine = _async_query_node_events_chunk(
            contract_address=contract_address,
            topics=topics,
            chunk_start=start_block,
            chunk_end=end_block,
            provider=provider,
            network=network,
            write_to_db=write_to_db,
        )
        coroutines.append(coroutine)

    chunks = await asyncio.gather(*coroutines)

    # return lists
    return pd.DataFrame(
        [log for chunk in chunks for response in chunk for log in response]
    )

    # # return dataframes
    # return pd.concat(chunks)

    # # possible should return list of dataframes
    # return chunks

    # # possible should return list of dataframes
    # return [log for chunk in chunks for response in chunk for log in response]


async def _async_query_node_events_chunk(
    *,
    contract_address: spec.Address | None,
    topics: typing.Sequence[typing.Any] | None,
    chunk_start: int,
    chunk_end: int,
    provider: spec.ProviderReference,
    network: spec.NetworkReference,
    write_to_db: bool,
    max_request_size: int = 2000,
) -> spec.DataFrame:
    """process a chunk"""

    import pandas as pd
    from ctc.toolbox import chunk_utils

    # break each meta chunk into requests
    chunk_requests = chunk_utils.range_to_chunks(
        chunk_start,
        chunk_end,
        max_request_size,
    )

    # request from node
    coroutines = []
    for request_start, request_end in chunk_requests:
        coroutine = await rpc.async_eth_get_logs(
            address=contract_address,
            topics=topics,
            start_block=request_start,
            end_block=request_end,
            provider=provider,
        )
        coroutines.append(coroutine)
    results = await asyncio.gather(*coroutines)

    # process raw events
    raw_logs = [event for result in results for event in result]
    encoded_events = await _async_process_raw_node_logs(raw_logs)

    # write encoded events to database
    if write_to_db:
        from ctc import db

        query: spec.EventQuery = {
            'contract_address': contract_address,
            'topics': topics,
            'start_block': chunk_start,
            'end_block': chunk_end,
        }
        await db.async_intake_encoded_events(
            encoded_events=encoded_events,
            query=query,
            network=network,
        )

    return pd.DataFrame(encoded_events)


async def _async_process_raw_node_logs(
    raw_logs: T,
) -> typing.Sequence[spec.EncodedEvent]:
    """convert from raw logs from node into encoded events for db"""
    if isinstance(raw_logs, list):
        return await _async_process_raw_node_logs_list(raw_logs)
    # elif type(raw_logs).__mro__[0].__name__ == 'DataFrame':
    #     return await _async_process_raw_node_logs_dataframe(raw_logs)
    else:
        raise Exception('unknown raw logs format')


async def _async_process_raw_node_logs_list(
    raw_logs: typing.Sequence[spec.RawLog],
) -> typing.Sequence[spec.EncodedEvent]:
    """modified in-place for performance"""
    for log in raw_logs:
        event = typing.cast(spec.EncodedEvent, log)
        event['contract_address'] = log.pop('address')  # type: ignore
        topics = log.pop('topics')  # type: ignore
        if topics is not None and len(topics) > 0:
            topic_iter = iter(topics)
            if len(topics) >= 1:
                event['event_hash'] = next(topic_iter)
            if len(topics) >= 2:
                event['topic1'] = next(topic_iter)
            if len(topics) >= 3:
                event['topic2'] = next(topic_iter)
            if len(topics) >= 4:
                event['topic3'] = next(topic_iter)
    return typing.cast(typing.Sequence[spec.EncodedEvent], raw_logs)


async def _async_process_raw_node_logs_dataframe(
    raw_logs: spec.DataFrame,
) -> spec.DataFrame:
    import pandas as pd

    split_topics = pd.DataFrame(
        raw_logs['topics'].to_list(),
        columns=['event_hash', 'topic1', 'topic2', 'topic3'],
    )
    encoded_events = pd.concat([raw_logs, split_topics], axis=1)
    encoded_events = encoded_events.rename(
        columns={'address': 'contract_address'}
    )
    return encoded_events
