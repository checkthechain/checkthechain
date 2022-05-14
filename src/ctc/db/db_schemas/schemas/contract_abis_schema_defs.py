from __future__ import annotations

import toolsql


contract_abis_schema: toolsql.DBSchema = {
    'tables': {
        'contract_abis': {
            'columns': [
                {'name': 'address', 'type': 'Text', 'primary': True},
                {'name': 'abi_text', 'type': 'Text'},
                {'name': 'includes_proxy', 'type': 'Text'},
            ],
        },
    },
}
