from __future__ import annotations

import toolsql


erc20_metadata_schema: toolsql.DBSchema = {
    'tables': {
        'erc20_metadata': {
            'columns': [
                {
                    'name': 'address',
                    'type': 'Text',
                    'primary': True,
                },
                {
                    'name': 'symbol',
                    'type': 'Text',
                    'index': True,
                },
                {
                    'name': 'decimals',
                    'type': 'Integer',
                },
                {
                    'name': 'name',
                    'type': 'Text',
                    'index': True,
                },
            ],
        },
    },
}
