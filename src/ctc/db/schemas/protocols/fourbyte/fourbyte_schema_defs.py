from __future__ import annotations

import toolsql

fourbyte_schema: toolsql.DBSchema = {
    'tables': {
        'function_signatures': {
            'columns': [
                {
                    'name': 'function_id',
                    'type': 'Integer',
                    'primary': True,
                },
                {
                    'name': 'function_hex',
                    'type': 'Text',
                    'index': True,
                },
                {
                    'name': 'function_text',
                    'type': 'Text',
                    'index': True,
                },
            ],
        },
        'event_signatures': {
            'columns': [
                {
                    'name': 'event_id',
                    'type': 'Integer',
                    'primary': True,
                },
                {
                    'name': 'event_hex',
                    'type': 'Text',
                    'index': True,
                },
                {
                    'name': 'event_text',
                    'type': 'Text',
                    'index': True,
                },
            ],
        },
    },
}
