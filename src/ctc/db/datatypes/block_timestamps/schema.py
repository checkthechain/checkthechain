import toolsql


def get_schema() -> toolsql.DBSchema:
    return {
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
                    },
                ],
            },
        },
    }

