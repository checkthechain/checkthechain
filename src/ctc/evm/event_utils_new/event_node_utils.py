from __future__ import annotations

import typing

from ctc import rpc
from ctc import spec
from .. import binary_utils
from . import event_query_utils

if typing.TYPE_CHECKING:
    T = typing.TypeVar('T', typing.Sequence[spec.RawLog], spec.DataFrame)

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
    write_to_db: bool,
    provider: spec.ProviderReference,
    verbose: bool | int,
    output_format: Literal['dataframe', 'dict'] = 'dataframe',
) -> spec.DataFrame | typing.Sequence[spec.EncodedEvent]:
    """query events from node and cache results in db if desired"""

    import asyncio
    from ctc.toolbox import range_utils

    query_type = event_query_utils._parse_event_query_type(
        contract_address=contract_address,
        event_hash=event_hash,
        topic1=topic1,
        topic2=topic2,
        topic3=topic3,
    )
    if query_type == 8:
        raise Exception('querying only by non-event-type topics is unsupported by some providers')

    network = rpc.get_provider_network(provider)

    topics = [topic1, topic2, topic3]
    print("ENCODED_TOPICS_INTERNAL:", topics)

    # break into chunks, each will be independently written to db
    chunk_size = 100000
    chunk_ranges = range_utils.range_to_chunks(
        start_block,
        end_block,
        chunk_size,
    )

    if verbose >= 1:
        n_blocks = end_block - start_block + 1
        print('fetching events from node over', n_blocks, 'blocks')
    if verbose >= 2:
        from ctc import cli

        event_query_utils.print_event_query_summary(
            contract_address=contract_address,
            event_hash=event_hash,
            topic1=topic1,
            topic2=topic2,
            topic3=topic3,
            start_block=start_block,
            end_block=end_block,
        )
        cli.print_bullet(key='network', value=network)
        cli.print_bullet(key='chunk_size', value=chunk_size)
        cli.print_bullet(key='n_chunks', value=len(chunk_ranges))

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
            provider=provider,
            network=network,
            write_to_db=write_to_db,
        )
        coroutines.append(coroutine)

    chunks = await asyncio.gather(*coroutines)

    result = [response for chunk in chunks for response in chunk]

    if verbose >= 2:
        print()
        print('events gathered')
        cli.print_bullet(key='n_events', value=len(result))
        n_contracts = len(set(event['contract_address'] for event in result))
        cli.print_bullet(key='n_contracts', value=n_contracts)
        n_event_types = len(set(event['event_hash'] for event in result))
        cli.print_bullet(key='n_event_types', value=n_event_types)

    if output_format == 'dict':
        return result
    elif output_format == 'dataframe':
        import pandas as pd

        df = pd.DataFrame(
            result,
            columns=spec.encoded_event_fields,
        )
        if 'removed' in df.columns:
            del df['removed']
        return df

    else:
        raise Exception('unknown output_format: ' + str(output_format))


async def _async_query_node_events_chunk(
    *,
    contract_address: spec.Address | None,
    event_hash: spec.BinaryData | None,
    topic1: spec.BinaryData | None,
    topic2: spec.BinaryData | None,
    topic3: spec.BinaryData | None,
    chunk_start: int,
    chunk_end: int,
    provider: spec.ProviderReference,
    network: spec.NetworkReference,
    write_to_db: bool,
    max_request_size: int = 2000,
) -> typing.Sequence[spec.EncodedEvent]:
    """process a chunk of events from node"""

    import asyncio
    from ctc.toolbox import range_utils

    # break each meta chunk into requests
    chunk_requests = range_utils.range_to_chunks(
        chunk_start,
        chunk_end,
        max_request_size,
    )

    if event_hash is not None:
        event_hash = binary_utils.binary_convert(event_hash, 'prefix_hex')
    if topic1 is not None:
        topic1 = binary_utils.binary_convert(topic1, 'prefix_hex')
    if topic2 is not None:
        topic2 = binary_utils.binary_convert(topic2, 'prefix_hex')
    if topic3 is not None:
        topic3 = binary_utils.binary_convert(topic3, 'prefix_hex')

    # request from node
    coroutines = []
    for request_start, request_end in chunk_requests:
        coroutine = rpc.async_eth_get_logs(
            address=contract_address,
            topics=[event_hash, topic1, topic2, topic3],
            start_block=request_start,
            end_block=request_end,
            provider=provider,
        )
        print("TPICSISCI", [event_hash, topic1, topic2, topic3])
        coroutines.append(coroutine)
    results = await asyncio.gather(*coroutines)

    # process raw events
    raw_logs = [event for result in results for event in result]
    encoded_events = await _async_process_raw_node_logs(raw_logs)

    # write encoded events to database
    if write_to_db:
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
            network=network,
        )

    return encoded_events


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
        event: spec.EncodedEvent = log  # type: ignore
        event['contract_address'] = log.pop('address')  # type: ignore
        event['unindexed'] = log.pop('data')  # type: ignore
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
    return raw_logs  # type: ignore


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
