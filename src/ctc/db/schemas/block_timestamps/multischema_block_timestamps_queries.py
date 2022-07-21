from __future__ import annotations

from ...management import active_utils
from ... import query_utils
from . import multischema_block_timestamps_statements
from . import multischema_block_timestamps_search


async_query_block_timestamp = query_utils.wrap_selector_with_connection(
    multischema_block_timestamps_statements.async_select_block_timestamp,
    active_utils.get_active_timestamp_schema,
)

async_query_block_timestamps = query_utils.wrap_selector_with_connection(
    multischema_block_timestamps_statements.async_select_block_timestamps,
    active_utils.get_active_timestamp_schema,
)

async_query_max_block_number = query_utils.wrap_selector_with_connection(
    multischema_block_timestamps_statements.async_select_max_block_number,
    active_utils.get_active_timestamp_schema,
)

async_query_max_block_timestamp = query_utils.wrap_selector_with_connection(
    multischema_block_timestamps_statements.async_select_max_block_timestamp,
    active_utils.get_active_timestamp_schema,
)

async_query_timestamp_block = query_utils.wrap_selector_with_connection(
    multischema_block_timestamps_search.async_select_timestamp_block,
    active_utils.get_active_timestamp_schema,
)

async_query_timestamps_blocks = query_utils.wrap_selector_with_connection(
    multischema_block_timestamps_search.async_select_timestamps_blocks,
    active_utils.get_active_timestamp_schema,
)

async_query_timestamp_block_range = query_utils.wrap_selector_with_connection(
    multischema_block_timestamps_search.async_select_timestamp_block_range,
    active_utils.get_active_timestamp_schema,
)
