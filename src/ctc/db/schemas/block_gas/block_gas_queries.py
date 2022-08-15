from __future__ import annotations

from ... import query_utils
from . import block_gas_statements


async_query_median_block_gas_fee = query_utils.wrap_selector_with_connection(
    block_gas_statements.async_select_median_block_gas_fee,
    'block_gas',
)

async_query_median_blocks_gas_fees = query_utils.wrap_selector_with_connection(
    block_gas_statements.async_select_median_blocks_gas_fees,
    'block_gas',
)
