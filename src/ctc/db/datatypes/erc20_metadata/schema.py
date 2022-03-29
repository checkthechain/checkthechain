from __future__ import annotations

import toolsql


def get_schema() -> toolsql.DBSchema:
    return {
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
                ],
            },
        },
    }

