from __future__ import annotations

from ... import query_utils
from . import transactions_statements


async_query_transaction = query_utils.wrap_selector_with_connection(
    transactions_statements.async_select_transaction,
    'transactions',
)

async_query_transactions = query_utils.wrap_selector_with_connection(
    transactions_statements.async_select_transactions,
    'transactions',
)

async_query_block_transaction_query = query_utils.wrap_selector_with_connection(
    transactions_statements.async_select_block_transaction_query,
    'transactions',
)

async_query_block_transaction_queries = (
    query_utils.wrap_selector_with_connection(
        transactions_statements.async_select_block_transaction_queries,
        'transactions',
    )
)

async_query_block_transactions = query_utils.wrap_selector_with_connection(
    transactions_statements.async_select_block_transactions,
    'transactions',
)

async_query_blocks_transactions = query_utils.wrap_selector_with_connection(
    transactions_statements.async_select_blocks_transactions,
    'transactions',
)

