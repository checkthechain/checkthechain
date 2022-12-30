from __future__ import annotations

from ctc import db
from . import coingecko_statements


async_query_token = db.wrap_selector_with_connection(
    coingecko_statements.async_select_token,
    'coingecko',
)

async_query_tokens = db.wrap_selector_with_connection(
    coingecko_statements.async_select_tokens,
    'coingecko',
)
