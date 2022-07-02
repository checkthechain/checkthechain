from __future__ import annotations

import toolsql

uniswap_v3_pools_schema: toolsql.DBSchema = {
    'tables': {
        'uniswap_v3_pools': {
            'columns': [
                {'name': 'address', 'type': 'Text', 'primary': True},
                {'name': 'token0', 'type': 'Text'},
                {'name': 'token1', 'type': 'Text'},
                {'name': 'fee', 'type': 'Text'},
            ],
        },
    },
}
