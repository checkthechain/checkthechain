from __future__ import annotations

import toolsql


contract_creation_blocks_schema: toolsql.DBSchema = {
    'tables': {
        'contract_creation_blocks': {
            'columns': [
                {
                    'name': 'address',
                    'type': 'Text',
                    'primary': True,
                },
                {
                    'name': 'block_number',
                    'type': 'Integer',
                    'index': True,
                },
            ],
        },
    },
}
