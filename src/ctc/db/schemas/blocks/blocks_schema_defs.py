from __future__ import annotations

import toolsql


blocks_schema: toolsql.DBSchema = {
    'tables': {
        'blocks': {
            'columns': [
                {'name': 'base_fee_per_gas', 'type': 'Text'},
                {'name': 'difficulty', 'type': 'Integer'},
                {'name': 'extra_data', 'type': 'Text'},
                {'name': 'gas_limit', 'type': 'Integer'},
                {'name': 'gas_used', 'type': 'Integer'},
                {'name': 'hash', 'type': 'Text', 'index': True},
                {'name': 'logs_bloom', 'type': 'Text'},
                {'name': 'miner', 'type': 'Text'},
                {'name': 'mix_hash', 'type': 'Text'},
                {'name': 'nonce', 'type': 'Text'},
                {'name': 'number', 'type': 'Integer', 'primary': True},
                {'name': 'parent_hash', 'type': 'Text'},
                {'name': 'receipts_root', 'type': 'Text'},
                {'name': 'sha3_uncles', 'type': 'Text'},
                {'name': 'size', 'type': 'Integer'},
                {'name': 'state_root', 'type': 'Text'},
                {'name': 'timestamp', 'type': 'Integer', 'index': True},
                {'name': 'total_difficulty', 'type': 'Text'},
                {'name': 'transactions', 'type': 'JSON'},
                {'name': 'transactions_root', 'type': 'Text'},
                {'name': 'uncles', 'type': 'JSON'},
            ],
        },
    },
}
