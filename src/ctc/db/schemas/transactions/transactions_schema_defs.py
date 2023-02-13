from __future__ import annotations

import toolsql


transactions_schema: toolsql.DBSchemaShorthand = {
    'tables': {
        'transactions': {
            'columns': [
                {'name': 'hash', 'type': 'Text', 'primary': True},
                {'name': 'block_number', 'type': 'Integer', 'index': True},
                {'name': 'transaction_index', 'type': 'Integer'},
                {'name': 'to_address', 'type': 'Text', 'index': True},
                {'name': 'from_address', 'type': 'Text', 'index': True},
                {'name': 'value', 'type': 'Text'},  # int <-> str
                {'name': 'input', 'type': 'Text'},
                {'name': 'nonce', 'type': 'Integer'},
                {'name': 'transaction_type', 'type': 'Integer'},
                {'name': 'status', 'type': 'Boolean'},  # from receipt
                {'name': 'gas_used', 'type': 'Integer'},  # from receipt
                {'name': 'gas_limit', 'type': 'Integer'},
                {'name': 'gas_priority', 'type': 'Integer', 'nullable': True},  # eip1559
                {'name': 'gas_price', 'type': 'Integer'},
                {'name': 'gas_price_max', 'type': 'Integer', 'nullable': True},  # eip1559
                {'name': 'access_list', 'type': 'JSON', 'nullable': True},  # type 1 and eip1559 tx
            ],
        },
        'block_transaction_queries': {
            'columns': [
                {'name': 'block_number', 'type': 'Integer', 'primary': True},
            ],
        },
    },
}

