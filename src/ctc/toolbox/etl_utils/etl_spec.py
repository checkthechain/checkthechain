contenttypes = {
    'Exporttype': [
        'blocks',
        'blocks_and_transactions',
        'token_transfers',
        'traces',
        'receipts_and_logs',
    ],
    'Rowtype': [
        'blocks',
        'transactions',
        'token_transfers',
        'traces',
        'receipts',
        'logs',
    ],
    'BlockChunk': ['BlockNumber', 'BlockNumber'],
    'ExistingRowData': {
        'mask_index': ['Integer'],
        'block_counts': 'IntegerArray',
        'path_ranges': {'Path': ['BlockNumber', 'BlockNumber']},
    },
}


rowtypes_of_exporttypes = {
    'blocks': ['blocks'],
    'blocks_and_transactions': ['blocks', 'transactions'],
    'token_transfers': ['token_transfers'],
    'traces': ['traces'],
    'receipts_and_logs': ['receipts', 'logs'],
}


# use **inclusive** names for both start and **end**, contrary to pythonicity
path_templates = {
    'blocks': '{etl_view}/blocks/blocks__{start_block}_to_{end_block}__{columns}.csv',
    'transactions': '{etl_view}/transactions/transactions__{start_block}_to_{end_block}__{columns}.csv',
    'token_transfers': '{etl_view}/token_transfers/token_transfers__{start_block}_to_{end_block}__{columns}.csv',
    'traces': '{etl_view}/traces/traces__{start_block}_to_{end_block}__{columns}.csv',
    'receipts': '{etl_view}/receipts/receipts__{start_block}_to_{end_block}__{columns}.csv',
    'logs': '{etl_view}/logs/logs__{start_block}_to_{end_block}__{columns}.csv',
}


command_templates = {
    'blocks': """
        python3 -m ethereumetl export_blocks_and_transactions \
        --start-block {start_block} \
        --end-block {end_block} \
        --blocks-output {blocks_path} \
        --provider-uri {provider}
    """,
    'blocks_and_transactions': """
        python3 -m ethereumetl export_blocks_and_transactions \
        --start-block {start_block} \
        --end-block {end_block} \
        --blocks-output {blocks_path} \
        --transactions-output {transactions_path} \
        --provider-uri {provider}
    """,
    'token_transfers': """
        python3 -m ethereumetl export_token_transfers \
        --start-block {start_block} \
        --end-block {end_block} \
        --provider-uri {provider} \
        --output {token_transfers_path}
    """,
    'traces': """
        python3 -m ethereumetl export_traces \
        --start-block {start_block} \
        --end-block {end_block} \
        --provider-uri {provider} \
        --output {traces_path}
    """,
    'receipts_and_logs': """
        ethereumetl export_receipts_and_logs \
        --transaction-hashes {transaction_hashes_path} \
        --provider-uri {provider} \
        --receipts-output {receipts_path} \
        --logs-output {logs_path}
    """,
}


block_number_columns = {
    'blocks': 'number',
    'transactions': 'block_number',
    'token_transfers': 'block_number',
    'traces': 'block_number',
    'receipts': 'block_number',
    'logs': 'block_number',
}

