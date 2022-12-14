from __future__ import annotations

import toolsql


transactions_schema: toolsql.DBSchema = {
    'tables': {
        'transactions': {
            'columns': [
                {'name': 'transaction_hash', 'type': 'Text', 'primary': True},
                {'name': 'block_number', 'type': 'Integer'},
                {'name': 'transaction_index', 'type': 'Integer'},
                {'name': 'to', 'type': 'Text'},
                {'name': 'from', 'type': 'Text'},
                {'name': 'value', 'type': 'Text'},  # int <-> str
                {'name': 'input', 'type': 'Text'},
                {'name': 'nonce', 'type': 'Integer'},
                {'name': 'type', 'type': 'Integer'},
                {'name': 'access_list', 'type': 'JSON'},

                # receipt related
                {'name': 'gas_used', 'type': 'Integer'},
                {'name': 'effective_gas_price', 'type': 'Text'},  # int <-> str
            ],
        },
        'block_transaction_queries': {
            'columns': [
                {'name': 'block_number', 'type': 'Integer', 'primary': True},
            ],
        },
    },
}

