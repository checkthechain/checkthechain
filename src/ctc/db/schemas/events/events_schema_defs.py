from __future__ import annotations

import toolsql


events_schema: toolsql.DBSchema = {
    'tables': {
        'events': {
            'columns': [
                {'name': 'block_number', 'type': 'Integer', 'primary': True},
                {'name': 'log_index', 'type': 'Integer', 'primary': True},
                {'name': 'transaction_hash', 'type': 'Text'},
                {'name': 'event_hash', 'type': 'Text'},
                {'name': 'topic0', 'type': 'Binary', 'index': True},
                {'name': 'topic1', 'type': 'Binary', 'index': True},
                {'name': 'topic2', 'type': 'Binary', 'index': True},
                {'name': 'topic3', 'type': 'Binary', 'index': True},
                {'name': 'unindexed', 'type': 'Binary'},
            ],
        },
        'events_contents': {
            'columns': [
                {'name': 'query_number', 'type': 'Integer', 'primary': True},
                {'name': 'contract_address', 'type': 'Integer', 'index': True},
                {'name': 'start_block', 'type': 'Integer', 'index': True},
                {'name': 'end_block', 'type': 'Integer', 'index': True},
                {'name': 'topic0', 'type': 'Binary', 'index': True},
                {'name': 'topic1', 'type': 'Binary', 'index': True},
                {'name': 'topic2', 'type': 'Binary', 'index': True},
                {'name': 'topic3', 'type': 'Binary', 'index': True},
                {'name': 'query_type', 'type': 'Integer', 'index': True},
            ],
        },
    },
}
