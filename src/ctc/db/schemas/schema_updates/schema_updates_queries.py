from __future__ import annotations

from ... import query_utils
from . import schema_updates_statements


async_query_schema_updates = query_utils.with_connection(
    schema_updates_statements.async_select_schema_updates,
    'schema_updates',
)
