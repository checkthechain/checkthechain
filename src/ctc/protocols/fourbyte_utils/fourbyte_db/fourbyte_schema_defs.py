from __future__ import annotations

import typing

if typing.TYPE_CHECKING:
    import toolsql


fourbyte_schema: toolsql.DBSchema = {
    'tables': {
        'function_signatures': {
            'columns': [
                {
                    'name': 'id',
                    'type': 'Integer',
                    'primary': True,
                },
                {
                    'name': 'created_at',
                    'type': 'Text',
                    'index': True,
                },
                {
                    'name': 'hex_signature',
                    'type': 'Text',
                    'index': True,
                },
                {
                    'name': 'text_signature',
                    'type': 'Text',
                    'index': True,
                },
                {
                    'name': 'bytes_signature',
                    'type': 'Text',
                    'index': True,
                },
            ],
        },
        'event_signatures': {
            'columns': [
                {
                    'name': 'id',
                    'type': 'Integer',
                    'primary': True,
                },
                {
                    'name': 'created_at',
                    'type': 'Text',
                    'index': True,
                },
                {
                    'name': 'hex_signature',
                    'type': 'Text',
                    'index': True,
                },
                {
                    'name': 'text_signature',
                    'type': 'Text',
                    'index': True,
                },
                {
                    'name': 'bytes_signature',
                    'type': 'Text',
                    'index': True,
                },
            ],
        },
    },
}
