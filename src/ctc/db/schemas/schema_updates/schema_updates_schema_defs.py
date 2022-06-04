from __future__ import annotations

import toolsql


schema_updates_schema: toolsql.DBSchema = {
    'tables': {
        'schema_updates': {
            'columns': [
                {'name': 'table_name', 'type': 'Text', 'primary': True},
                {'name': 'version', 'type': 'Text', 'primary': True},
                {
                    'name': 'timestamp',
                    'type': 'Timestamp',
                    'index': True,
                    'created_time': True,
                },
            ],
        },
    },
}
