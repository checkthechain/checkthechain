from __future__ import annotations

import toolsql

block_gas_stats_schema: toolsql.DBSchema = {
    'tables': {
        'block_gas_stats': {
            'columns': [
                {'name': 'block_number', 'type': 'Integer', 'primary': True},
                {'name': 'base', 'type': 'Integer'},
                {'name': 'mean', 'type': 'Integer'},
                {'name': 'median', 'type': 'Integer'},
                {'name': 'min', 'type': 'Integer'},
                {'name': 'max', 'type': 'Integer'},
                {'name': 'p1', 'type': 'Integer'},
                {'name': 'p5', 'type': 'Integer'},
                {'name': 'p10', 'type': 'Integer'},
                {'name': 'p25', 'type': 'Integer'},
                {'name': 'p75', 'type': 'Integer'},
                {'name': 'p90', 'type': 'Integer'},
                {'name': 'p95', 'type': 'Integer'},
                {'name': 'p99', 'type': 'Integer'},
                {'name': 'limit', 'type': 'Integer'},
                {'name': 'used', 'type': 'Integer'},
                {'name': 'n_transactions', 'type': 'Integer'},
            ],
        },
    },
}
