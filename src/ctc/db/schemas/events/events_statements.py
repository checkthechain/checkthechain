from __future__ import annotations

import typing

from ctc import spec
from ... import schema_utils

if typing.TYPE_CHECKING:
    import toolsql


async def async_upsert_events(
    *,
    encoded_events: typing.Sequence[spec.EncodedEvent] | spec.DataFrame,
    conn: toolsql.SAConnection,
    network: spec.NetworkReference,
) -> None:

    if spec.is_dataframe(encoded_events):
        encoded_events = encoded_events.to_dict('records')  # type: ignore
    encoded_events = typing.cast(typing.Sequence[spec.EncodedEvent], encoded_events)

    table = schema_utils.get_table_name('events', network=network)
    toolsql.insert(
        conn=conn,
        table=table,
        rows=encoded_events,
        upsert='do_update',
    )


async def async_upsert_event_query(
    *,
    query: spec.EventQuery,
    conn: toolsql.SAConnection,
    network: spec.NetworkReference,
) -> None:

    table = schema_utils.get_table_name('event_queries', network=network)
    toolsql.insert(
        conn=conn,
        table=table,
        row=query,
        upsert='do_update',
    )
