from __future__ import annotations

import toolsql


fourbyte_schema: toolsql.DBSchema = {
    'tables': {
        'function_signatures': {
            'columns': [
                {'name': 'id', 'primary': True},
                {'name': 'created_at'},
                {'name': 'text_signature', 'index': True},
                {'name': 'hex_signature', 'index': True},
                {'name': 'bytes_signature'},
            ],
        },
        'event_signatures': {
            'columns': [
                {'name': 'id', 'primary': True},
                {'name': 'created_at'},
                {'name': 'text_signature', 'index': True},
                {'name': 'hex_signature', 'index': True},
                {'name': 'bytes_signature'},
            ],
        },
    },
}
