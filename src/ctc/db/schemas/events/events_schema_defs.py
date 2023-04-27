from __future__ import annotations

import toolsql


_event_binary_fields = [
    'contract_address',
    'transaction_hash',
    'event_hash',
    'topic1',
    'topic2',
    'topic3',
    'unindexed',
]

_event_query_binary_fields = [
    'contract_address',
    'event_hash',
    'topic1',
    'topic2',
    'topic3',
]

events_schema: toolsql.DBSchemaShorthand = {
    'tables': {
        'events': {
            'columns': [
                {
                    'name': 'block_number',
                    'type': 'Integer',
                    'primary': True,
                    'nullable': False,
                },
                {
                    'name': 'transaction_index',
                    'type': 'Integer',
                    'primary': True,
                    'nullable': False,
                },
                {
                    'name': 'log_index',
                    'type': 'Integer',
                    'primary': True,
                    'nullable': False,
                },
                {
                    'name': 'transaction_hash',
                    'type': 'Binary',
                    'nullable': False,
                },
                {'name': 'contract_address', 'type': 'Binary', 'index': True},
                {'name': 'event_hash', 'type': 'Binary', 'index': True},
                {'name': 'topic1', 'type': 'Binary', 'index': True},
                {'name': 'topic2', 'type': 'Binary', 'index': True},
                {'name': 'topic3', 'type': 'Binary', 'index': True},
                {'name': 'unindexed', 'type': 'Binary'},
                {'name': 'decoded', 'type': 'JSON'},
            ],
        },
        'event_queries': {
            'columns': [
                {
                    'name': 'query_id',
                    'type': 'Integer',
                    'primary': True,
                    'autoincrement': True,
                },
                {'name': 'contract_address', 'type': 'Binary', 'index': True},
                {
                    'name': 'start_block',
                    'type': 'Integer',
                    'index': True,
                    'nullable': False,
                },
                {
                    'name': 'end_block',
                    'type': 'Integer',
                    'index': True,
                    'nullable': False,
                },
                {'name': 'event_hash', 'type': 'Binary', 'index': True},
                {'name': 'topic1', 'type': 'Binary', 'index': True},
                {'name': 'topic2', 'type': 'Binary', 'index': True},
                {'name': 'topic3', 'type': 'Binary', 'index': True},
                {
                    'name': 'query_type',
                    'type': 'Integer',
                    'index': True,
                    'nullable': False,
                },
            ],
        },
    },
}

