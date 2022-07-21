from __future__ import annotations

from ... import query_utils
from . import contract_abis_statements


async_query_contract_abi = query_utils.wrap_selector_with_connection(
    contract_abis_statements.async_select_contract_abi,
    'contract_abis',
)

async_query_contract_abis = query_utils.wrap_selector_with_connection(
    contract_abis_statements.async_select_contract_abis,
    'contract_abis',
)
