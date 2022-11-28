from __future__ import annotations

from .. import query_utils
from . import events_statements


async_query_events = query_utils.wrap_selector_with_connection(
    events_statements.async_select_events,
    'events',
)


async_query_event_queries = query_utils.wrap_selector_with_connection(
    events_statements.async_select_event_queries,
    'events',
)
