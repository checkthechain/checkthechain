from __future__ import annotations

from .. import query_utils
from . import contract_creation_blocks_statements


async_query_contract_creation_block = query_utils.with_connection(
    contract_creation_blocks_statements.async_select_contract_creation_block,
    'contract_creation_blocks',
)


async_query_contract_creation_blocks = query_utils.with_connection(
    contract_creation_blocks_statements.async_select_contract_creation_blocks,
    'contract_creation_blocks',
)
