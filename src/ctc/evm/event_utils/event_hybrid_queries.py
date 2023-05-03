"""
see ctc.db.schemas.events.events_intake for db writing functions
"""
from __future__ import annotations

import typing

from ctc import spec
from . import event_node_utils
from . import event_query_utils

if typing.TYPE_CHECKING:
    from typing_extensions import Literal


async def _async_plan_event_query(
    *,
    contract_address: spec.Address | None,
    event_hash: bytes | None,
    topic1: bytes | None,
    topic2: bytes | None,
    topic3: bytes | None,
    start_block: int,
    end_block: int,
    context: spec.Context = None,
) -> spec.EventQueryPlan:
    """plan which parts of query should be dispatched to db vs node"""

    from ctc import config
    from ctc import db
    from ctc.toolbox import range_utils

    # parse query type
    query_type = event_query_utils._parse_event_query_type(
        contract_address=contract_address,
        event_hash=event_hash,
        topic1=topic1,
        topic2=topic2,
        topic3=topic3,
    )

    # get previous queries
    read_cache, write_cache = config.get_context_cache_read_write(
        schema_name='events', context=context
    )
    if not read_cache:
        db_ranges: typing.Sequence[typing.Sequence[int]] = []
    else:
        db_queries = await db.async_query_event_queries(
            query_type=query_type,
            contract_address=contract_address,
            event_hash=event_hash,
            topic1=topic1,
            topic2=topic2,
            topic3=topic3,
            context=context,
            start_block=start_block,
            end_block=end_block,
        )
        if db_queries is not None:
            db_ranges = []
            for db_query in db_queries:
                db_start_block = db_query['start_block']
                db_end_block = db_query['end_block']
                if db_start_block <= start_block:
                    db_start_block = start_block
                if db_end_block >= end_block:
                    db_end_block = end_block
                db_ranges.append((db_start_block, db_end_block))

        else:
            db_ranges = []

    # get overlap between current query range and previous query ranges
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
    event_hash: bytes | None,
    topic1: bytes | None,
    topic2: bytes | None,
    topic3: bytes | None,
    start_block: int,
    end_block: int,
    context: spec.Context,
    verbose: bool | int,
    columns_to_load: typing.Sequence[str],
    binary_output_format: Literal['binary', 'prefix_hex'] = 'binary',
    max_blocks_per_request: int = 2000,
) -> spec.DataFrame:

    import polars as pl
    from ctc import db
    from ctc.toolbox import pl_utils

    # check which portion of query is in db
    queries = await _async_plan_event_query(
        contract_address=contract_address,
        event_hash=event_hash,
        topic1=topic1,
        topic2=topic2,
        topic3=topic3,
        start_block=start_block,
        end_block=end_block,
        context=context,
    )

    if verbose >= 2:
        print('Query Plan:')
        print('- db queries:', len(queries['db']))
        print('- node queries:', len(queries['node']))

    results: typing.MutableMapping[int, spec.DataFrame] = {}

    # TODO: query from db and node in parallel

    # send db queries to db
    for query in queries['db']:
        db_result: spec.DataFrame | None = await db.async_query_events(
            context=context,
            binary_output_format=binary_output_format,
            columns=columns_to_load,
            output_format='polars',
            **query,
        )

        if db_result is None:
            continue

        # adjust types
        recast_bools = pl.col(pl.datatypes.Boolean).cast(pl.datatypes.Utf8)
        db_result = db_result.with_columns(db_result.select(recast_bools))
        if binary_output_format == 'prefix_hex':
            db_result = pl_utils.binary_columns_to_prefix_hex(db_result)

        results[query['start_block']] = db_result

    # send node queries to node
    for query in queries['node']:

        result = await event_node_utils._async_query_events_from_node(
            context=context,
            verbose=verbose,
            binary_output_format=binary_output_format,
            max_blocks_per_request=max_blocks_per_request,
            **query,
        )

        # omit unwanted columns
        for key in {
            'transaction_index',
            'log_index',
            'transaction_hash',
            'contract_address',
            'event_hash',
            'topic1',
            'topic2',
            'topic3',
            'unindexed',
        }:
            if key not in columns_to_load:
                result = result.drop(key)

        if binary_output_format == 'binary':
            result = pl_utils.prefix_hex_columns_to_binary(result)

        results[query['start_block']] = result

    sorted_results = [results[key] for key in sorted(results.keys())]
    events = pl.concat(sorted_results)

    return events

