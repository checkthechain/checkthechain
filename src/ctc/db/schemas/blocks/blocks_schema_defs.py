from __future__ import annotations

import toolsql


blocks_schema: toolsql.DBSchemaShorthand = {
    'tables': {
        'blocks': {
            'columns': [
                {'name': 'number', 'type': 'Integer', 'primary': True},
                {'name': 'hash', 'type': 'Text', 'index': True},
                {'name': 'timestamp', 'type': 'Integer', 'index': True},
                {'name': 'miner', 'type': 'Text'},
                {'name': 'extra_data', 'type': 'Text'},
                {'name': 'base_fee_per_gas', 'type': 'Integer', 'nullable': True},  # post-eip1559
                {'name': 'gas_limit', 'type': 'Integer'},
                {'name': 'gas_used', 'type': 'Integer'},
            ],
        },
    },
}
