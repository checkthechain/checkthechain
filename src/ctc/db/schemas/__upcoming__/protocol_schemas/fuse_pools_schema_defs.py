from __future__ import annotations

import toolsql

fuse_pools_schema: toolsql.DBSchema = {
    'tables': {
        'fuse_pools': {
            'columns': [
                {'name': 'index', 'type': 'Integer', 'primary': True},
                {'name': 'comptroller', 'type': 'Text', 'index': True},
            ],
        },
        'fuse_ftokens': {
            'columns': [
                {'name': 'address', 'type': 'Text', 'primary': True},
                {'name': 'underyling', 'type': 'Text', 'index': True},
                {'name': 'comptroller', 'type': 'Text', 'index': True},
            ],
        },
    },
}
