"""
see ctc.db.schemas.events.events_intake for db writing functions
"""
from __future__ import annotations

import typing

from ctc import spec
from . import event_node_utils
from . import event_query_utils


async def _async_plan_event_query(
    *,
    contract_address: spec.Address | None,
    event_hash: typing.Any | None,
    topic1: typing.Any | None,
    topic2: typing.Any | None,
    topic3: typing.Any | None,
    start_block: int,
    end_block: int,
    network: spec.NetworkReference,
) -> spec.EventQueryPlan:
    """plan which parts of query should be dispatched to db vs node"""

    from ctc import db
    from ctc.toolbox import range_utils

    # get previous queries
    query_type = event_query_utils._parse_event_query_type(
        contract_address=contract_address,
        event_hash=event_hash,
        topic1=topic1,
        topic2=topic2,
        topic3=topic3,
    )
    db_queries = await db.async_query_event_queries(
        query_type=query_type,
        contract_address=contract_address,
        event_hash=event_hash,
        topic1=topic1,
        topic2=topic2,
        topic3=topic3,
        network=network,
        start_block=start_block,
        end_block=end_block,
    )
    if db_queries is not None:
        for db_query in db_queries:
            del db_query['query_id']
            del db_query['query_type']  # type: ignore
            if db_query['start_block'] <= start_block:
                db_query['start_block'] = start_block
            if db_query['end_block'] >= end_block:
                db_query['end_block'] = end_block
    else:
        db_queries = []

    # get overlap between current query range and previous query ranges
    db_ranges: typing.Sequence[typing.Sequence[int]] = [
        [db_query['start_block'], db_query['end_block']]
        for db_query in db_queries
    ]
    db_ranges = range_utils.combine_overlapping_ranges(
        db_ranges,
        include_contiguous=True,
    )
    node_ranges = range_utils.get_range_gaps(
        start=start_block,
        end=end_block,
        subranges=db_ranges,
    )
    db_event_queries: typing.Sequence[spec.EventQuery] = [
        {
            'contract_address': contract_address,
            'event_hash': event_hash,
            'topic1': topic1,
            'topic2': topic2,
            'topic3': topic3,
            'start_block': db_start,
            'end_block': db_end,
        }
        for db_start, db_end in db_ranges
    ]

    # queries
    node_queries: typing.Sequence[spec.EventQuery] = [
        {
            'contract_address': contract_address,
            'event_hash': event_hash,
            'topic1': topic1,
            'topic2': topic2,
            'topic3': topic3,
            'start_block': node_start,
            'end_block': node_end,
        }
        for node_start, node_end in node_ranges
    ]

    return {
        'node': node_queries,
        'db': db_event_queries,
    }


async def _async_query_events_from_node_and_db(
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
    network: spec.NetworkReference,
    verbose: bool | int,
) -> typing.Sequence[spec.EncodedEvent] | spec.DataFrame:

    from ctc import db

    # check which portion of query is in db
    queries = await _async_plan_event_query(
        contract_address=contract_address,
        event_hash=event_hash,
        topic1=topic1,
        topic2=topic2,
        topic3=topic3,
        start_block=start_block,
        end_block=end_block,
        network=network,
    )

    if verbose >= 2:
        print('Query Plan:')
        print('- db queries:', len(queries['db']))
        print('- node queries:', len(queries['node']))

    results: typing.MutableMapping[int, spec.DataFrame] = {}

    # send db queries to db
    for query in queries['db']:
        db_result = await db.async_query_events(network=network, **query)
        if db_result is None:
            raise Exception('could not obtain results from db')
        elif spec.is_dataframe(db_result):
            results[query['start_block']] = db_result
        else:
            raise Exception('unknown db_result format: ' + str(type(db_result)))

    # send node queries to node
    for query in queries['node']:
        import pandas as pd

        result = await event_node_utils._async_query_events_from_node(
            write_to_db=write_to_db,
            provider=provider,
            verbose=verbose,
            output_format='dataframe',
            **query,
        )
        results[query['start_block']] = pd.DataFrame(result)

    sorted_results = [results[key] for key in sorted(results.keys())]
    import pandas as pd

    events = pd.concat(sorted_results)
    # events = [event for result in sorted_results for event in result]

    return events
