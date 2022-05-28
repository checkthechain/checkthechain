from __future__ import annotations

from ... import query_utils
from . import blocks_statements


async_query_block = query_utils.with_connection(
    blocks_statements.async_select_block,
    'blocks',
)

async_query_blocks = query_utils.with_connection(
    blocks_statements.async_select_blocks,
    'blocks',
)
