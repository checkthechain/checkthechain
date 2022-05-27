from __future__ import annotations

import toolsql


meta_schema_schema: toolsql.DBSchema = {
    'tables': {
        'schema_update_history': {
            'columns': [
                {'name': 'table_name', 'type': 'Text', 'primary': True},
                {'name': 'version', 'type': 'Text', 'primary': True},
                {
                    'name': 'timestamp',
                    'type': 'Timestamp',
                    'index': True,
                    'modified_time': True,
                },
            ],
        },
    },
}
