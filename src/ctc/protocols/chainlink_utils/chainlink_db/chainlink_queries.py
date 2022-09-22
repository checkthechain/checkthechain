from __future__ import annotations

from ctc import db

from . import chainlink_statements


async_query_feed = db.query_utils.wrap_selector_with_connection(
    chainlink_statements.async_select_feed,
    'chainlink',
)

async_query_feeds = db.query_utils.wrap_selector_with_connection(
    chainlink_statements.async_select_feeds,
    'chainlink',
)

async_query_aggregator_updates = db.query_utils.wrap_selector_with_connection(
    chainlink_statements.async_select_aggregator_updates,
    'chainlink',
)
