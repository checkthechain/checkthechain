from __future__ import annotations

import toolsql

dex_pools_schema: toolsql.DBSchema = {
    'tables': {
        'dex_pools': {
            'columns': [
                {'name': 'address', 'type': 'Text', 'primary': True},
                {'name': 'factory', 'type': 'Text', 'index': True},
                {'name': 'asset0', 'type': 'Text', 'index': True},
                {'name': 'asset1', 'type': 'Text', 'index': True},
                {'name': 'asset2', 'type': 'Text', 'index': True},
                {'name': 'asset3', 'type': 'Text', 'index': True},
                {'name': 'creation_block', 'type': 'Integer', 'index': True},
                {'name': 'fee', 'type': 'Integer'},
                {'name': 'additional_data', 'type': 'JSON'},
                {'name': 'priority', 'type': 'Integer', 'index': True},
            ],
        },
        'dex_pool_factory_queries': {
            'columns': [
                {'name': 'factory', 'type': 'Text', 'primary': True},
                {'name': 'last_scanned_block', 'type': 'Integer'},
            ],
        },
    },
}
