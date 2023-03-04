from __future__ import annotations

import toolsql


block_timestamps_schema: toolsql.DBSchemaShorthand = {
    'tables': {
        'block_timestamps': {
            'columns': [
                {
                    'name': 'block_number',
                    'type': 'Integer',
                    'primary': True,
                },
                {
                    'name': 'timestamp',
                    'type': 'Integer',
                    'index': True,
                    'nullable': False,
                },
            ],
        },
    },
}
