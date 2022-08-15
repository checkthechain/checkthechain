from __future__ import annotations

import toolsql


block_gas_schema: toolsql.DBSchema = {
    'tables': {
        'block_gas': {
            'columns': [
                {
                    'name': 'block_number',
                    'type': 'Integer',
                    'primary': True,
                },
                {
                    'name': 'timestamp',
                    'type': 'Integer',
                    'index': True,
                },
                {
                    'name': 'median_gas_fee',
                    'type': 'Float',
                },
            ],
        },
    },
}
