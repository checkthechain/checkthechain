from __future__ import annotations

import toolsql


meta_schema_schema: toolsql.DBSchema = {
    'tables': {
        'schema_versions': {
            'columns': [
                {'name': 'ctc_version', 'type': 'Text', 'primary': True},
                {'name': 'timestamp', 'type': 'Timestamp', 'index': True},
            ],
        },
    },
}
