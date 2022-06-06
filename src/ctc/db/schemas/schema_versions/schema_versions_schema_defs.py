from __future__ import annotations

import toolsql


schema_versions_schema: toolsql.DBSchema = {
    'tables': {
        'schema_versions': {
            'columns': [
                {'name': 'schema_name', 'type': 'Text', 'primary': True},
                # use chain_id==-1 for schemas that are not related to a particular chain
                {'name': 'chain_id', 'type': 'Integer', 'primary': True},
                {'name': 'version', 'type': 'Text'},
            ],
        },
    },
}
