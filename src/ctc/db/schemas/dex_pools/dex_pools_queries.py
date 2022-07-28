from __future__ import annotations

from .. import query_utils
from . import dex_pools_statements


async_query_dex_pool = query_utils.wrap_selector_with_connection(
    dex_pools_statements.async_select_dex_pool,
    'dex_pools',
)


async_query_dex_pools = query_utils.wrap_selector_with_connection(
    dex_pools_statements.async_select_dex_pools,
    'dex_pools',
)

async_query_dex_pool_factory_last_scanned_block = (
    query_utils.wrap_selector_with_connection(
        dex_pools_statements.async_select_dex_pool_factory_last_scanned_block,
        'dex_pools',
    )
)
