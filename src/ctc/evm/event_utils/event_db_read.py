from __future__ import annotations

import typing

from ctc import spec
from . import event_node_read


async def _async_query_events_from_node_and_db(
    *,
    contract_address: spec.Address | None,
    topics: typing.Sequence[typing.Any] | None,
    start_block: int,
    end_block: int,
    write_to_db: bool,
    provider: spec.ProviderReference,
) -> spec.DataFrame:

    import pandas as pd

    # check which portion of query is in db
    queries = await _async_create_db_and_node_queries(
        contract_address=contract_address,
        topics=topics,
        start_block=start_block,
        end_block=end_block,
    )

    results: typing.MutableMapping[int, spec.DataFrame] = {}

    # send db queries to db
    for query in queries['db']:
        results[query['start_block']] = await _async_query_events_from_db(
            contract_address=contract_address,
            topics=topics,
            start_block=start_block,
            end_block=end_block,
        )

    # send node queries to node
    for query in queries['node']:
        results[
            query['start_block']
        ] = await event_node_read._async_query_events_from_node(
            contract_address=contract_address,
            topics=topics,
            start_block=start_block,
            end_block=end_block,
            write_to_db=write_to_db,
            provider=provider,
        )

    sorted_results = [results[key] for key in sorted(results.keys())]
    events = pd.concat(sorted_results)

    return events


async def _async_create_db_and_node_queries(
    *,
    contract_address: spec.Address | None,
    topics: typing.Sequence[typing.Any] | None,
    start_block: int,
    end_block: int,
) -> spec.EventQueryRoute:
    return {
        'node': [],
        'db': [],
    }


async def _async_query_events_from_db(
    *,
    contract_address: spec.Address | None,
    topics: typing.Sequence[typing.Any] | None,
    start_block: int,
    end_block: int,
) -> spec.DataFrame:
    raise NotImplementedError()
