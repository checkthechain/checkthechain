from __future__ import annotations

from ctc import db

from ..fourbyte_db import fourbyte_statements


async_query_local_function_signatures = db.wrap_selector_with_connection(
    fourbyte_statements.async_select_function_signatures,
    '4byte',
    require_network=False,
)

async_query_local_event_signatures = db.wrap_selector_with_connection(
    fourbyte_statements.async_select_event_signatures,
    '4byte',
    require_network=False,
)
