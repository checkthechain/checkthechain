from __future__ import annotations

import toolsql


erc20_state_schema: toolsql.DBSchema = {
    'tables': {
        'erc20_balances': {
            'columns': [
                {
                    'name': 'erc20',
                    'type': 'Text',
                    'primary': True,
                },
                {
                    'name': 'wallet',
                    'type': 'Text',
                    'primary': True,
                },
                {
                    'name': 'block',
                    'type': 'Integer',
                    'primary': True,
                },
                {
                    'name': 'balance',
                    'type': 'Text',
                },
            ],
        },
        'erc20_total_supplies': {
            'columns': [
                {
                    'name': 'erc20',
                    'type': 'Text',
                    'index': True,
                },
                {
                    'name': 'block',
                    'type': 'Integer',
                    'index': True,
                },
                {
                    'name': 'total_supply',
                    'type': 'Text',
                },
            ],
        },
    },
}
