from __future__ import annotations

from .. import query_utils
from . import erc20_metadata_statements


async_query_erc20_metadata = query_utils.with_connection(
    erc20_metadata_statements.async_select_erc20_metadata,
    'erc20_metadata',
)


async_query_erc20_metadatas = query_utils.with_connection(
    erc20_metadata_statements.async_select_erc20_metadatas,
    'erc20_metadata',
)
