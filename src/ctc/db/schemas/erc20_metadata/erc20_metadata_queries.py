from __future__ import annotations

from .. import query_utils
from . import erc20_metadata_statements


async_query_erc20_metadata = query_utils.wrap_selector_with_connection(
    erc20_metadata_statements.async_select_erc20_metadata,
    'erc20_metadata',
    require_network=False,
)


async_query_erc20s_metadata = query_utils.wrap_selector_with_connection(
    erc20_metadata_statements.async_select_erc20s_metadata,
    'erc20_metadata',
    require_network=False,
)
